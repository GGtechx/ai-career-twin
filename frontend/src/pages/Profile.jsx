import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { profileAPI, authAPI, getUser } from '../services/api';
import {
  Sparkles, User, GraduationCap, Building2, BookOpen, Award, Briefcase,
  Code, Brain, MessageSquare, Target, Compass, Save, LogOut, CheckCircle2,
  AlertCircle, Plus, Trash2, ExternalLink, Loader2, FileText,
  Layers, ShieldCheck, Zap
} from 'lucide-react';

export default function Profile() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  // Profile Form State
  const [profile, setProfile] = useState({
    full_name: '',
    email: '',
    college_name: '',
    degree: 'B.Tech',
    branch: 'CSE',
    cgpa: 7.5,
    college_tier: 'Tier 2',
    current_year: 3,
    current_semester: 6,
    graduation_year: 2026,
    roll_number: '',
    phone: '',
    technical_skills: [],
    soft_skills: [],
    programming_languages: [],
    coding_score: 65.0,
    aptitude_score: 65.0,
    communication_score: 65.0,
    projects: [],
    certifications: [],
    internships: [],
    interests: [],
    career_goal: '',
    target_company: '',
    target_job_role: '',
    bio: '',
    linkedin_url: '',
    github_url: '',
    leetcode_url: '',
    portfolio_url: ''
  });

  // Tag inputs state
  const [newTechSkill, setNewTechSkill] = useState('');
  const [newProgLang, setNewProgLang] = useState('');
  const [newSoftSkill, setNewSoftSkill] = useState('');
  const [newInterest, setNewInterest] = useState('');

  // Project input state
  const [newProject, setNewProject] = useState({ title: '', tech_stack: '', description: '' });
  // Certification input state
  const [newCert, setNewCert] = useState({ title: '', issuer: '' });
  // Internship input state
  const [newIntern, setNewIntern] = useState({ company: '', role: '', duration_months: 3 });

  useEffect(() => {
    fetchProfileData();
  }, []);

  const fetchProfileData = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const data = await profileAPI.getProfile();
      setProfile(prev => ({
        ...prev,
        ...data,
        cgpa: data.cgpa || 0.0,
        technical_skills: data.technical_skills || [],
        soft_skills: data.soft_skills || [],
        programming_languages: data.programming_languages || [],
        projects: data.projects || [],
        certifications: data.certifications || [],
        internships: data.internships || [],
        interests: data.interests || []
      }));
    } catch (err) {
      setErrorMsg(err.message || 'Failed to load profile.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type } = e.target;
    setProfile(prev => ({
      ...prev,
      [name]: type === 'number' ? (parseFloat(value) || 0) : value
    }));
    if (successMsg) setSuccessMsg('');
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setErrorMsg('');
    setSuccessMsg('');

    try {
      const updated = await profileAPI.updateProfile(profile);
      setProfile(prev => ({ ...prev, ...updated }));
      setSuccessMsg('Profile successfully updated and saved in the live PostgreSQL database!');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      setErrorMsg(err.message || 'Failed to save profile changes.');
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = async () => {
    await authAPI.logout();
    navigate('/login');
  };

  // Tag Helpers
  const addTag = (field, value, setter) => {
    if (!value.trim()) return;
    const clean = value.trim();
    if (!profile[field].includes(clean)) {
      setProfile(prev => ({ ...prev, [field]: [...prev[field], clean] }));
    }
    setter('');
  };

  const removeTag = (field, index) => {
    setProfile(prev => ({
      ...prev,
      [field]: prev[field].filter((_, i) => i !== index)
    }));
  };

  // Project Helpers
  const addProject = () => {
    if (!newProject.title.trim()) return;
    const techArray = newProject.tech_stack.split(',').map(s => s.trim()).filter(Boolean);
    const item = {
      title: newProject.title.trim(),
      tech_stack: techArray,
      description: newProject.description.trim()
    };
    setProfile(prev => ({ ...prev, projects: [...prev.projects, item] }));
    setNewProject({ title: '', tech_stack: '', description: '' });
  };

  const removeProject = (index) => {
    setProfile(prev => ({
      ...prev,
      projects: prev.projects.filter((_, i) => i !== index)
    }));
  };

  // Certification Helpers
  const addCertification = () => {
    if (!newCert.title.trim()) return;
    const item = { title: newCert.title.trim(), issuer: newCert.issuer.trim() };
    setProfile(prev => ({ ...prev, certifications: [...prev.certifications, item] }));
    setNewCert({ title: '', issuer: '' });
  };

  const removeCertification = (index) => {
    setProfile(prev => ({
      ...prev,
      certifications: prev.certifications.filter((_, i) => i !== index)
    }));
  };

  // Internship Helpers
  const addInternship = () => {
    if (!newIntern.company.trim()) return;
    const item = {
      company: newIntern.company.trim(),
      role: newIntern.role.trim() || 'Intern',
      duration_months: parseInt(newIntern.duration_months) || 3
    };
    setProfile(prev => ({ ...prev, internships: [...prev.internships, item] }));
    setNewIntern({ company: '', role: '', duration_months: 3 });
  };

  const removeInternship = (index) => {
    setProfile(prev => ({
      ...prev,
      internships: prev.internships.filter((_, i) => i !== index)
    }));
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div style={{ textAlign: 'center' }}>
          <Loader2 size={36} className="animate-spin" style={{ color: 'var(--primary)', margin: '0 auto 1rem' }} />
          <p style={{ color: 'var(--text-muted)', fontWeight: 500 }}>Loading student profile from database...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen" style={{ paddingBottom: '4rem' }}>
      
      {/* Universal Top Navbar */}
      <Navbar />

      {/* Main Content */}
      <div className="container" style={{ marginTop: '1.5rem' }}>
        
        {/* Page Title & Actions */}
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '1rem', marginBottom: '1.5rem' }}>
          <div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 0.25rem 0' }}>
              Student Profile
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', margin: 0 }}>
              Manage your academic records, technical skills, experiences, and career goals.
            </p>
          </div>

          <button
            onClick={handleSave}
            disabled={saving}
            className="btn btn-primary"
            style={{ padding: '0.75rem 1.5rem', fontSize: '0.9rem' }}
          >
            {saving ? (
              <>
                <Loader2 size={18} className="animate-spin" />
                Saving to Database...
              </>
            ) : (
              <>
                <Save size={18} />
                Save Profile Changes
              </>
            )}
          </button>
        </div>

        {/* Notifications */}
        {successMsg && (
          <div className="alert alert-success">
            <CheckCircle2 size={18} style={{ flexShrink: 0 }} />
            <span>{successMsg}</span>
          </div>
        )}

        {errorMsg && (
          <div className="alert alert-error">
            <AlertCircle size={18} style={{ flexShrink: 0 }} />
            <span>{errorMsg}</span>
          </div>
        )}

        <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
          
          {/* Section 1: Academic & Personal Info */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.25rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.75rem' }}>
              <GraduationCap size={22} style={{ color: '#2563eb' }} />
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Academic & Demographic Records</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="form-group">
                <label className="form-label">Full Name</label>
                <input
                  type="text"
                  name="full_name"
                  className="form-input"
                  value={profile.full_name || ''}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Email (System Login)</label>
                <input
                  type="email"
                  name="email"
                  disabled
                  className="form-input"
                  style={{ background: '#f8fafc', color: '#64748b' }}
                  value={profile.email || ''}
                />
              </div>

              <div className="form-group">
                <label className="form-label">College / University Name</label>
                <input
                  type="text"
                  name="college_name"
                  className="form-input"
                  value={profile.college_name || ''}
                  onChange={handleInputChange}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Degree</label>
                <input
                  type="text"
                  name="degree"
                  className="form-input"
                  placeholder="e.g. B.Tech"
                  value={profile.degree || ''}
                  onChange={handleInputChange}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Branch / Department</label>
                <input
                  type="text"
                  name="branch"
                  className="form-input"
                  placeholder="e.g. Computer Science & Engineering"
                  value={profile.branch || ''}
                  onChange={handleInputChange}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Cumulative GPA (CGPA: 0.0 - 10.0)</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="10"
                  name="cgpa"
                  className="form-input"
                  value={profile.cgpa}
                  onChange={handleInputChange}
                />
              </div>

              <div className="form-group">
                <label className="form-label">College Tier</label>
                <select
                  name="college_tier"
                  className="form-select"
                  value={profile.college_tier || 'Tier 2'}
                  onChange={handleInputChange}
                >
                  <option value="Tier 1">Tier 1 (IIT / NIT / BITS / Premier)</option>
                  <option value="Tier 2">Tier 2 (State Govt / Autonomous)</option>
                  <option value="Tier 3">Tier 3 (Affiliated / Private)</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Current Academic Year</label>
                <select
                  name="current_year"
                  className="form-select"
                  value={profile.current_year || 3}
                  onChange={handleInputChange}
                >
                  <option value={1}>1st Year</option>
                  <option value={2}>2nd Year</option>
                  <option value={3}>3rd Year</option>
                  <option value={4}>4th Year (Final Year)</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Roll Number / Student ID</label>
                <input
                  type="text"
                  name="roll_number"
                  placeholder="e.g. 2022CSB104"
                  className="form-input"
                  value={profile.roll_number || ''}
                  onChange={handleInputChange}
                />
              </div>
            </div>
          </div>

          {/* Section 2: Skills Inventory */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.25rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.75rem' }}>
              <Code size={22} style={{ color: '#8b5cf6' }} />
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Skills & Programming Languages</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              
              {/* Technical Skills */}
              <div>
                <label className="form-label">Technical Skills (Frameworks, Databases, Tools)</label>
                <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
                  <input
                    type="text"
                    placeholder="e.g. FastAPI, Docker"
                    className="form-input"
                    value={newTechSkill}
                    onChange={(e) => setNewTechSkill(e.target.value)}
                    onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addTag('technical_skills', newTechSkill, setNewTechSkill); }}}
                  />
                  <button
                    type="button"
                    onClick={() => addTag('technical_skills', newTechSkill, setNewTechSkill)}
                    className="btn btn-secondary"
                  >
                    <Plus size={16} />
                  </button>
                </div>

                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', minHeight: '60px', padding: '0.5rem', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                  {profile.technical_skills.map((skill, idx) => (
                    <span key={idx} className="tag-removable">
                      {skill}
                      <button type="button" onClick={() => removeTag('technical_skills', idx)}>&times;</button>
                    </span>
                  ))}
                  {profile.technical_skills.length === 0 && (
                    <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>No technical skills added yet.</span>
                  )}
                </div>
              </div>

              {/* Programming Languages */}
              <div>
                <label className="form-label">Programming Languages</label>
                <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
                  <input
                    type="text"
                    placeholder="e.g. Python, C++, Java"
                    className="form-input"
                    value={newProgLang}
                    onChange={(e) => setNewProgLang(e.target.value)}
                    onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addTag('programming_languages', newProgLang, setNewProgLang); }}}
                  />
                  <button
                    type="button"
                    onClick={() => addTag('programming_languages', newProgLang, setNewProgLang)}
                    className="btn btn-secondary"
                  >
                    <Plus size={16} />
                  </button>
                </div>

                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', minHeight: '60px', padding: '0.5rem', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                  {profile.programming_languages.map((lang, idx) => (
                    <span key={idx} className="tag-removable" style={{ background: '#ede9fe', color: '#6b21a8' }}>
                      {lang}
                      <button type="button" onClick={() => removeTag('programming_languages', idx)}>&times;</button>
                    </span>
                  ))}
                  {profile.programming_languages.length === 0 && (
                    <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>No languages added.</span>
                  )}
                </div>
              </div>

              {/* Soft Skills */}
              <div>
                <label className="form-label">Soft Skills & Competencies</label>
                <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
                  <input
                    type="text"
                    placeholder="e.g. Problem Solving, Agile"
                    className="form-input"
                    value={newSoftSkill}
                    onChange={(e) => setNewSoftSkill(e.target.value)}
                    onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addTag('soft_skills', newSoftSkill, setNewSoftSkill); }}}
                  />
                  <button
                    type="button"
                    onClick={() => addTag('soft_skills', newSoftSkill, setNewSoftSkill)}
                    className="btn btn-secondary"
                  >
                    <Plus size={16} />
                  </button>
                </div>

                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', minHeight: '60px', padding: '0.5rem', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                  {profile.soft_skills.map((skill, idx) => (
                    <span key={idx} className="tag-removable" style={{ background: '#d1fae5', color: '#065f46' }}>
                      {skill}
                      <button type="button" onClick={() => removeTag('soft_skills', idx)}>&times;</button>
                    </span>
                  ))}
                  {profile.soft_skills.length === 0 && (
                    <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>No soft skills added.</span>
                  )}
                </div>
              </div>

            </div>
          </div>

          {/* Section 3: Performance Assessment Scores */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.25rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.75rem' }}>
              <Brain size={22} style={{ color: '#10b981' }} />
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Performance Assessment Scores (0 - 100)</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              
              <div style={{ background: '#f8fafc', padding: '1.25rem', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <span style={{ fontWeight: 600, fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <Code size={16} style={{ color: '#2563eb' }} />
                    Coding Performance
                  </span>
                  <span style={{ fontWeight: 700, color: '#2563eb', fontSize: '1.1rem' }}>
                    {profile.coding_score}
                  </span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  name="coding_score"
                  value={profile.coding_score}
                  onChange={handleInputChange}
                  style={{ width: '100%', accentColor: '#2563eb', cursor: 'pointer' }}
                />
                <p style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.35rem' }}>
                  Evaluates algorithm proficiency, LeetCode solved problems, and code quality.
                </p>
              </div>

              <div style={{ background: '#f8fafc', padding: '1.25rem', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <span style={{ fontWeight: 600, fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <Brain size={16} style={{ color: '#8b5cf6' }} />
                    Aptitude & Logic
                  </span>
                  <span style={{ fontWeight: 700, color: '#8b5cf6', fontSize: '1.1rem' }}>
                    {profile.aptitude_score}
                  </span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  name="aptitude_score"
                  value={profile.aptitude_score}
                  onChange={handleInputChange}
                  style={{ width: '100%', accentColor: '#8b5cf6', cursor: 'pointer' }}
                />
                <p style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.35rem' }}>
                  Quantitative problem-solving, logical deductions, and data interpretation.
                </p>
              </div>

              <div style={{ background: '#f8fafc', padding: '1.25rem', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <span style={{ fontWeight: 600, fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <MessageSquare size={16} style={{ color: '#10b981' }} />
                    Communication Score
                  </span>
                  <span style={{ fontWeight: 700, color: '#10b981', fontSize: '1.1rem' }}>
                    {profile.communication_score}
                  </span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  name="communication_score"
                  value={profile.communication_score}
                  onChange={handleInputChange}
                  style={{ width: '100%', accentColor: '#10b981', cursor: 'pointer' }}
                />
                <p style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.35rem' }}>
                  Verbal clarity, mock interview articulation, and interpersonal presentation.
                </p>
              </div>

            </div>
          </div>

          {/* Section 4: Career Goals & Target Companies */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.25rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.75rem' }}>
              <Target size={22} style={{ color: '#f59e0b' }} />
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Career Targets & Aspirations</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="form-group">
                <label className="form-label">Target Dream Company</label>
                <input
                  type="text"
                  name="target_company"
                  placeholder="e.g. Google, Microsoft, Amazon, Atlassian"
                  className="form-input"
                  value={profile.target_company || ''}
                  onChange={handleInputChange}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Target Job Role</label>
                <input
                  type="text"
                  name="target_job_role"
                  placeholder="e.g. Software Development Engineer, Full Stack Developer"
                  className="form-input"
                  value={profile.target_job_role || ''}
                  onChange={handleInputChange}
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Career Goal Vision</label>
              <textarea
                name="career_goal"
                placeholder="State your mid-term and long-term career ambition..."
                className="form-textarea"
                value={profile.career_goal || ''}
                onChange={handleInputChange}
              />
            </div>
          </div>

          {/* Section 5: Projects & Experience Lists */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.25rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.75rem' }}>
              <Briefcase size={22} style={{ color: '#0ea5e9' }} />
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Projects, Certifications & Internships</h2>
            </div>

            {/* Projects Sub-section */}
            <div style={{ marginBottom: '1.75rem' }}>
              <h3 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#334155', marginBottom: '0.6rem' }}>
                Key Technical Projects ({profile.projects.length})
              </h3>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr auto', gap: '0.5rem', marginBottom: '0.75rem' }}>
                <input
                  type="text"
                  placeholder="Project Title"
                  className="form-input"
                  value={newProject.title}
                  onChange={(e) => setNewProject(p => ({ ...p, title: e.target.value }))}
                />
                <input
                  type="text"
                  placeholder="Tech Stack (comma-separated, e.g. React, FastAPI)"
                  className="form-input"
                  value={newProject.tech_stack}
                  onChange={(e) => setNewProject(p => ({ ...p, tech_stack: e.target.value }))}
                />
                <button type="button" onClick={addProject} className="btn btn-secondary">
                  <Plus size={16} /> Add Project
                </button>
              </div>

              {profile.projects.map((proj, idx) => (
                <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.75rem', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0', marginBottom: '0.5rem' }}>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{proj.title}</div>
                    <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                      Stack: {Array.isArray(proj.tech_stack) ? proj.tech_stack.join(', ') : proj.tech_stack}
                    </div>
                  </div>
                  <button type="button" onClick={() => removeProject(idx)} className="btn btn-danger" style={{ padding: '0.35rem 0.6rem' }}>
                    <Trash2 size={14} />
                  </button>
                </div>
              ))}
            </div>

            {/* Certifications & Internships grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* Certifications */}
              <div>
                <h3 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#334155', marginBottom: '0.6rem' }}>
                  Certifications ({profile.certifications.length})
                </h3>
                <div style={{ display: 'flex', gap: '0.4rem', marginBottom: '0.6rem' }}>
                  <input
                    type="text"
                    placeholder="Certificate Title"
                    className="form-input"
                    value={newCert.title}
                    onChange={(e) => setNewCert(c => ({ ...c, title: e.target.value }))}
                  />
                  <input
                    type="text"
                    placeholder="Issuer (AWS, Google)"
                    className="form-input"
                    value={newCert.issuer}
                    onChange={(e) => setNewCert(c => ({ ...c, issuer: e.target.value }))}
                  />
                  <button type="button" onClick={addCertification} className="btn btn-secondary">
                    <Plus size={16} />
                  </button>
                </div>

                {profile.certifications.map((cert, idx) => (
                  <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.5rem 0.75rem', background: '#f8fafc', borderRadius: '6px', border: '1px solid #e2e8f0', marginBottom: '0.4rem' }}>
                    <div style={{ fontSize: '0.85rem' }}>
                      <span style={{ fontWeight: 600 }}>{cert.title}</span>
                      {cert.issuer && <span style={{ color: '#64748b' }}> ({cert.issuer})</span>}
                    </div>
                    <button type="button" onClick={() => removeCertification(idx)} className="btn btn-danger" style={{ padding: '0.2rem 0.4rem' }}>
                      <Trash2 size={12} />
                    </button>
                  </div>
                ))}
              </div>

              {/* Internships */}
              <div>
                <h3 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#334155', marginBottom: '0.6rem' }}>
                  Internships ({profile.internships.length})
                </h3>
                <div style={{ display: 'flex', gap: '0.4rem', marginBottom: '0.6rem' }}>
                  <input
                    type="text"
                    placeholder="Company Name"
                    className="form-input"
                    value={newIntern.company}
                    onChange={(e) => setNewIntern(i => ({ ...i, company: e.target.value }))}
                  />
                  <input
                    type="text"
                    placeholder="Role"
                    className="form-input"
                    value={newIntern.role}
                    onChange={(e) => setNewIntern(i => ({ ...i, role: e.target.value }))}
                  />
                  <button type="button" onClick={addInternship} className="btn btn-secondary">
                    <Plus size={16} />
                  </button>
                </div>

                {profile.internships.map((intern, idx) => (
                  <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.5rem 0.75rem', background: '#f8fafc', borderRadius: '6px', border: '1px solid #e2e8f0', marginBottom: '0.4rem' }}>
                    <div style={{ fontSize: '0.85rem' }}>
                      <span style={{ fontWeight: 600 }}>{intern.company}</span>
                      <span style={{ color: '#64748b' }}> - {intern.role} ({intern.duration_months} mo)</span>
                    </div>
                    <button type="button" onClick={() => removeInternship(idx)} className="btn btn-danger" style={{ padding: '0.2rem 0.4rem' }}>
                      <Trash2 size={12} />
                    </button>
                  </div>
                ))}
              </div>

            </div>
          </div>

          {/* Bottom Save Bar */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '1rem' }}>
            <button
              type="submit"
              disabled={saving}
              className="btn btn-primary"
              style={{ padding: '0.85rem 2rem', fontSize: '1rem', boxShadow: '0 4px 14px 0 rgba(37,99,235,0.39)' }}
            >
              {saving ? (
                <>
                  <Loader2 size={18} className="animate-spin" />
                  Saving to Live Database...
                </>
              ) : (
                <>
                  <Save size={18} />
                  Save Complete Profile
                </>
              )}
            </button>
          </div>

        </form>
      </div>
    </div>
  );
}
