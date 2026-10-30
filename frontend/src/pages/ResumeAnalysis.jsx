import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import ActiveTargetIndicator from '../components/ActiveTargetIndicator';
import { useCareerTarget } from '../context/CareerTargetContext';
import { resumeAPI, profileAPI, authAPI } from '../services/api';
import {
  UploadCloud, FileText, CheckCircle2, AlertTriangle, AlertCircle,
  Sparkles, Award, Briefcase, GraduationCap, Code, ArrowRight,
  RefreshCw, Loader2, LogOut, Check, ExternalLink, User,
  BarChart3, ShieldCheck, Zap, Info, Plus, Building2, Layers, Target
} from 'lucide-react';

export default function ResumeAnalysis() {
  const navigate = useNavigate();
  const { activeTarget } = useCareerTarget();
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [syncingSkills, setSyncingSkills] = useState(false);

  // Analysis & Resume State
  const [resumeData, setResumeData] = useState(null);
  const [activeTab, setActiveTab] = useState('overview'); // 'overview' | 'skills' | 'projects' | 'education' | 'experience'

  useEffect(() => {
    fetchLatestAnalysis();
  }, []);

  const fetchLatestAnalysis = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const data = await resumeAPI.getAnalysis();
      setResumeData(data);
    } catch (err) {
      // 404 means no resume uploaded yet, which is expected for new students
      const msg = (err?.message || '').toLowerCase();
      if (msg.includes('not found') || msg.includes('no resume')) {
        setResumeData(null);
      } else {
        setErrorMsg(err.message || 'Failed to load resume analysis.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await authAPI.logout();
    navigate('/login');
  };

  // Drag and drop handlers
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelected(e.target.files[0]);
    }
  };

  const handleFileSelected = (file) => {
    setErrorMsg('');
    setSuccessMsg('');
    if (!file.name.toLowerCase().endsWith('.pdf') && file.type !== 'application/pdf') {
      setErrorMsg('Invalid file type. Please upload a PDF file (.pdf).');
      setSelectedFile(null);
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setErrorMsg('File too large. Maximum allowed size is 5 MB.');
      setSelectedFile(null);
      return;
    }
    if (file.size === 0) {
      setErrorMsg('The selected PDF file is empty.');
      setSelectedFile(null);
      return;
    }
    setSelectedFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setErrorMsg('Please select a PDF resume file to upload.');
      return;
    }

    setUploading(true);
    setErrorMsg('');
    setSuccessMsg('');

    try {
      const uploadResult = await resumeAPI.uploadResume(selectedFile);
      setSuccessMsg(`Resume "${uploadResult.file_name}" uploaded and analyzed successfully! ATS Score: ${uploadResult.ats_score}% (${uploadResult.ats_rating})`);
      setSelectedFile(null);
      // Fetch full structured analysis
      await fetchLatestAnalysis();
    } catch (err) {
      setErrorMsg(err.message || 'Resume upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  // 1-Click Sync Missing Skills to Student Profile
  const handleSyncSkillsToProfile = async (skillsToAdd) => {
    if (!skillsToAdd || skillsToAdd.length === 0) return;
    setSyncingSkills(true);
    try {
      const currentProfile = await profileAPI.getProfile();
      const currentTech = currentProfile.technical_skills || [];
      const updatedTech = Array.from(new Set([...currentTech, ...skillsToAdd]));
      
      await profileAPI.updateProfile({
        ...currentProfile,
        technical_skills: updatedTech
      });

      setSuccessMsg(`Added ${skillsToAdd.length} skill(s) to your Career Twin profile!`);
      // Refresh analysis to update comparison
      await fetchLatestAnalysis();
    } catch (err) {
      setErrorMsg(`Failed to sync skills to profile: ${err.message}`);
    } finally {
      setSyncingSkills(false);
    }
  };

  // Helper for score badge colors
  const getScoreColor = (score) => {
    if (score >= 80) return { bg: '#dcfce7', text: '#15803d', border: '#bbf7d0', bar: '#16a34a' };
    if (score >= 65) return { bg: '#dbeafe', text: '#1d4ed8', border: '#bfdbfe', bar: '#2563eb' };
    if (score >= 50) return { bg: '#fef3c7', text: '#b45309', border: '#fde68a', bar: '#d97706' };
    return { bg: '#fee2e2', text: '#b91c1c', border: '#fecaca', bar: '#dc2626' };
  };

  return (
    <div className="min-h-screen" style={{ paddingBottom: '4rem' }}>
      
      {/* Universal Top Navbar */}
      <Navbar />

      {/* Main Content Area */}
      <div className="container" style={{ marginTop: '1.5rem' }}>
        
        {/* Page Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
          <div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 0.25rem 0' }}>
              Resume Analysis
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', margin: 0 }}>
              Upload your PDF resume to check ATS readiness, extract skills, and identify missing keywords for your target role.
            </p>
          </div>
          <div>
            <ActiveTargetIndicator />
          </div>
        </div>

        {/* Global Alerts */}
        {errorMsg && (
          <div className="alert alert-error" style={{ marginBottom: '1.5rem' }}>
            <AlertCircle size={20} style={{ flexShrink: 0 }} />
            <span>{errorMsg}</span>
          </div>
        )}

        {successMsg && (
          <div className="alert alert-success" style={{ marginBottom: '1.5rem' }}>
            <CheckCircle2 size={20} style={{ flexShrink: 0 }} />
            <span>{successMsg}</span>
          </div>
        )}

        {/* Upload Card */}
        <div className="card" style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1rem' }}>
            <UploadCloud size={22} style={{ color: '#2563eb' }} />
            <h2 style={{ fontSize: '1.15rem', fontWeight: 700, margin: 0 }}>
              Upload Resume (PDF)
            </h2>
          </div>

          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            style={{
              border: `2px dashed ${dragActive ? 'var(--primary)' : 'var(--border)'}`,
              backgroundColor: dragActive ? 'var(--primary-light)' : 'var(--bg-subtle)',
              borderRadius: '12px',
              padding: '2.5rem 1.5rem',
              textAlign: 'center',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              marginBottom: '1rem'
            }}
            onClick={() => document.getElementById('resume-file-input').click()}
          >
            <input
              id="resume-file-input"
              type="file"
              accept=".pdf,application/pdf"
              style={{ display: 'none' }}
              onChange={handleFileChange}
            />

            <div style={{
              width: '56px',
              height: '56px',
              borderRadius: '50%',
              background: 'var(--primary-light)',
              color: 'var(--primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1rem'
            }}>
              <UploadCloud size={28} />
            </div>

            <p style={{ fontWeight: 600, fontSize: '0.975rem', color: 'var(--text-main)', marginBottom: '0.35rem' }}>
              Drag & Drop your resume PDF here, or <span style={{ color: 'var(--primary)', textDecoration: 'underline' }}>browse</span>
            </p>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
              Supports PDF format only (Max 5 MB).
            </p>

            {selectedFile && (
              <div style={{
                marginTop: '1.25rem',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.6rem',
                padding: '0.5rem 1rem',
                background: 'var(--bg-card)',
                border: '1px solid var(--border)',
                borderRadius: '8px',
                fontSize: '0.85rem',
                color: 'var(--text-main)'
              }}>
                <FileText size={16} />
                <span style={{ fontWeight: 600 }}>{selectedFile.name}</span>
                <span style={{ color: 'var(--text-muted)' }}>({(selectedFile.size / 1024).toFixed(1)} KB)</span>
              </div>
            )}
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
            {selectedFile && (
              <button
                type="button"
                onClick={() => setSelectedFile(null)}
                className="btn btn-secondary"
                disabled={uploading}
              >
                Clear
              </button>
            )}

            <button
              type="button"
              onClick={handleUpload}
              disabled={!selectedFile || uploading}
              className="btn btn-primary"
              style={{ padding: '0.65rem 1.5rem' }}
            >
              {uploading ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  Extracting & Analyzing PDF...
                </>
              ) : (
                <>
                  <Zap size={16} />
                  Analyze Resume
                </>
              )}
            </button>
          </div>
        </div>

        {/* Loading Spinner for Analysis Data */}
        {loading && (
          <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
            <Loader2 size={32} className="animate-spin" style={{ color: 'var(--primary)', margin: '0 auto 1rem' }} />
            <p style={{ color: 'var(--text-muted)', fontWeight: 500 }}>Loading latest resume analysis...</p>
          </div>
        )}

        {/* Empty State when no resume uploaded */}
        {!loading && !resumeData && (
          <div className="card" style={{ textAlign: 'center', padding: '3.5rem 2rem' }}>
            <div style={{
              width: '64px',
              height: '64px',
              borderRadius: '50%',
              background: 'var(--bg-subtle)',
              color: 'var(--text-muted)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1rem'
            }}>
              <FileText size={32} />
            </div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
              No Resume Uploaded Yet
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', maxWidth: '480px', margin: '0 auto 1.5rem' }}>
              Upload your engineering or technical resume above to get instant NLP parsing, ATS completeness scoring, and profile synchronization.
            </p>
          </div>
        )}

        {/* Active Analysis Dashboard */}
        {!loading && resumeData && (
          <div>
            
            {/* Top Score & Summary Banner */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6" style={{ marginBottom: '2rem' }}>
              
              {/* ATS Score Card */}
              <div className="card" style={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                background: 'var(--bg-card)',
                borderLeft: `5px solid ${getScoreColor(resumeData.ats_score).bar}`
              }}>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                    <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                      ATS Completeness Score
                    </span>
                    <span style={{
                      padding: '0.2rem 0.6rem',
                      borderRadius: '999px',
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      backgroundColor: getScoreColor(resumeData.ats_score).bg,
                      color: getScoreColor(resumeData.ats_score).text
                    }}>
                      {resumeData.ats_rating}
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem', marginBottom: '0.75rem' }}>
                    <span style={{ fontSize: '2.75rem', fontWeight: 900, color: 'var(--text-main)', lineHeight: 1 }}>
                      {Math.round(resumeData.ats_score)}
                    </span>
                    <span style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-dim)' }}>/ 100</span>
                  </div>

                  {/* Progress bar */}
                  <div style={{ width: '100%', height: '8px', background: 'var(--border)', borderRadius: '999px', overflow: 'hidden', marginBottom: '0.75rem' }}>
                    <div style={{
                      width: `${Math.min(100, Math.max(0, resumeData.ats_score))}%`,
                      height: '100%',
                      background: getScoreColor(resumeData.ats_score).bar,
                      borderRadius: '999px',
                      transition: 'width 0.6s ease'
                    }} />
                  </div>
                </div>

                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', justifyContent: 'space-between' }}>
                  <span>Words: {resumeData.word_count || 0}</span>
                  <span>Exp: {resumeData.extracted_experience_years || 0} yrs</span>
                </div>
              </div>

              {/* Candidate Info Card */}
              <div className="card" style={{ gridColumn: 'span 2' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', borderBottom: '1px solid var(--border)', paddingBottom: '0.75rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <ShieldCheck size={20} style={{ color: 'var(--primary)' }} />
                    <h3 style={{ fontSize: '1rem', fontWeight: 700, margin: 0, color: 'var(--text-main)' }}>
                      Extracted Candidate Information
                    </h3>
                  </div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    File: <strong style={{ color: 'var(--text-main)' }}>{resumeData.file_name}</strong>
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3" style={{ fontSize: '0.85rem' }}>
                  <div>
                    <span style={{ color: 'var(--text-muted)' }}>Name: </span>
                    <strong style={{ color: 'var(--text-main)' }}>{resumeData.extracted_name || 'Not detected'}</strong>
                  </div>
                  <div>
                    <span style={{ color: 'var(--text-muted)' }}>Email: </span>
                    <strong style={{ color: 'var(--text-main)' }}>{resumeData.extracted_email || 'Not detected'}</strong>
                  </div>
                  <div>
                    <span style={{ color: 'var(--text-muted)' }}>Phone: </span>
                    <strong style={{ color: 'var(--text-main)' }}>{resumeData.extracted_phone || 'Not detected'}</strong>
                  </div>
                  <div>
                    <span style={{ color: 'var(--text-muted)' }}>LinkedIn: </span>
                    {resumeData.extracted_linkedin ? (
                      <a href={resumeData.extracted_linkedin} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary)', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '0.2rem' }}>
                        Profile <ExternalLink size={12} />
                      </a>
                    ) : (
                      <span style={{ color: 'var(--text-dim)' }}>Missing</span>
                    )}
                  </div>
                  <div>
                    <span style={{ color: 'var(--text-muted)' }}>GitHub: </span>
                    {resumeData.extracted_github ? (
                      <a href={resumeData.extracted_github} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary)', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '0.2rem' }}>
                        Profile <ExternalLink size={12} />
                      </a>
                    ) : (
                      <span style={{ color: 'var(--text-dim)' }}>Missing</span>
                    )}
                  </div>
                  <div>
                    <span style={{ color: 'var(--text-muted)' }}>Analyzed: </span>
                    <span style={{ color: 'var(--text-main)' }}>{new Date(resumeData.uploaded_at).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>

            </div>

            {/* ATS Category Breakdown */}
            {resumeData.ats_breakdown && (
              <div className="card" style={{ marginBottom: '2rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.25rem' }}>
                  <BarChart3 size={20} style={{ color: '#2563eb' }} />
                  <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: 0 }}>
                    ATS Scoring Category Breakdown
                  </h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {Object.entries(resumeData.ats_breakdown).map(([category, detail]) => {
                    const pct = Math.round((detail.score / detail.max) * 100);
                    return (
                      <div key={category} style={{ background: '#f8fafc', padding: '1rem', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem', fontSize: '0.85rem' }}>
                          <span style={{ fontWeight: 600, color: '#1e293b' }}>{category}</span>
                          <span style={{ fontWeight: 700, color: '#2563eb' }}>{detail.score} / {detail.max}</span>
                        </div>
                        <div style={{ width: '100%', height: '6px', background: '#e2e8f0', borderRadius: '999px', overflow: 'hidden' }}>
                          <div style={{ width: `${pct}%`, height: '100%', background: '#2563eb', borderRadius: '999px' }} />
                        </div>
                        {detail.feedback && detail.feedback.length > 0 && (
                          <div style={{ marginTop: '0.5rem', fontSize: '0.75rem', color: '#b45309' }}>
                            {detail.feedback[0]}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Target Job Keyword Alignment Box */}
            {activeTarget && (
              <div className="card" style={{ marginBottom: '1.5rem', background: 'linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)', border: '1px solid #93c5fd' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', flexWrap: 'wrap', gap: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Target size={20} style={{ color: '#2563eb' }} />
                    <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#1e3a8a', margin: 0 }}>
                      Target Job Keyword Alignment: {activeTarget.job_title} at {activeTarget.company_name}
                    </h3>
                  </div>
                  <span className="badge badge-blue">Active Career Target</span>
                </div>
                <p style={{ fontSize: '0.85rem', color: '#1e40af', marginBottom: '1rem' }}>
                  Comparing skills parsed from your resume against must-have technical requirements for <strong>{activeTarget.job_title}</strong> at <strong>{activeTarget.company_name}</strong>.
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div style={{ background: '#ffffff', padding: '1rem', borderRadius: '10px', border: '1px solid #bfdbfe' }}>
                    <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#16a34a', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <CheckCircle2 size={16} /> Target Skills Matched in Resume
                    </div>
                    {(() => {
                      const matched = (activeTarget.required_skills || []).filter(s =>
                        (resumeData.extracted_skills || []).some(es => es.toLowerCase() === s.toLowerCase())
                      );
                      return matched.length > 0 ? (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                          {matched.map((s, idx) => (
                            <span key={idx} className="badge badge-green" style={{ fontSize: '0.8rem' }}>✓ {s}</span>
                          ))}
                        </div>
                      ) : (
                        <div style={{ fontSize: '0.8rem', color: '#64748b' }}>No direct keyword matches yet.</div>
                      );
                    })()}
                  </div>

                  <div style={{ background: '#ffffff', padding: '1rem', borderRadius: '10px', border: '1px solid #fecaca' }}>
                    <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#dc2626', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <AlertCircle size={16} /> Target Skills Missing from Resume
                    </div>
                    {(() => {
                      const missing = (activeTarget.required_skills || []).filter(s =>
                        !(resumeData.extracted_skills || []).some(es => es.toLowerCase() === s.toLowerCase())
                      );
                      return missing.length > 0 ? (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                          {missing.map((s, idx) => (
                            <span key={idx} className="badge badge-red" style={{ fontSize: '0.8rem' }}>⚠️ {s}</span>
                          ))}
                        </div>
                      ) : (
                        <div style={{ fontSize: '0.8rem', color: '#16a34a' }}>All target skills present in resume!</div>
                      );
                    })()}
                  </div>
                </div>
              </div>
            )}

            {/* Profile Comparison & Missing Info Section */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6" style={{ marginBottom: '2rem' }}>
              
              {/* Box 1: Skills in Resume but missing from Profile */}
              <div className="card" style={{ borderTop: '4px solid #10b981' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Plus size={18} style={{ color: '#10b981' }} />
                    <h3 style={{ fontSize: '0.95rem', fontWeight: 700, margin: 0 }}>
                      Skills in Resume (Missing from Profile)
                    </h3>
                  </div>

                  {resumeData.skills_to_add_to_profile && resumeData.skills_to_add_to_profile.length > 0 && (
                    <button
                      onClick={() => handleSyncSkillsToProfile(resumeData.skills_to_add_to_profile)}
                      disabled={syncingSkills}
                      className="btn btn-primary"
                      style={{ padding: '0.3rem 0.7rem', fontSize: '0.75rem' }}
                    >
                      {syncingSkills ? 'Syncing...' : 'Add All to Profile'}
                    </button>
                  )}
                </div>

                <p style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: '1rem' }}>
                  These skills were identified in your resume but have not been added to your Career Twin profile.
                </p>

                {resumeData.skills_to_add_to_profile && resumeData.skills_to_add_to_profile.length > 0 ? (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                    {resumeData.skills_to_add_to_profile.map((skill, i) => (
                      <span key={i} className="badge badge-green" style={{ fontSize: '0.8rem', padding: '0.3rem 0.65rem' }}>
                        + {skill}
                      </span>
                    ))}
                  </div>
                ) : (
                  <div style={{ color: '#10b981', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.4rem', background: '#f0fdf4', padding: '0.75rem', borderRadius: '8px' }}>
                    <CheckCircle2 size={16} /> All resume skills are already represented in your profile!
                  </div>
                )}
              </div>

              {/* Box 2: Skills in Profile but missing from Resume */}
              <div className="card" style={{ borderTop: '4px solid #f59e0b' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                  <AlertTriangle size={18} style={{ color: '#f59e0b' }} />
                  <h3 style={{ fontSize: '0.95rem', fontWeight: 700, margin: 0 }}>
                    Skills in Profile (Missing from Resume)
                  </h3>
                </div>

                <p style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: '1rem' }}>
                  These skills are in your student profile, but ATS keyword matching didn't detect them in your uploaded resume.
                </p>

                {resumeData.skills_missing_from_resume && resumeData.skills_missing_from_resume.length > 0 ? (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                    {resumeData.skills_missing_from_resume.map((skill, i) => (
                      <span key={i} className="badge badge-amber" style={{ fontSize: '0.8rem', padding: '0.3rem 0.65rem' }}>
                        ⚠️ {skill}
                      </span>
                    ))}
                  </div>
                ) : (
                  <div style={{ color: '#15803d', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.4rem', background: '#f0fdf4', padding: '0.75rem', borderRadius: '8px' }}>
                    <CheckCircle2 size={16} /> All profile skills are present in your resume text!
                  </div>
                )}
              </div>

            </div>

            {/* Missing Important Profile Information Box */}
            {resumeData.missing_profile_info && resumeData.missing_profile_info.length > 0 && (
              <div className="card" style={{ marginBottom: '2rem', backgroundColor: '#fffbeb', border: '1px solid #fde68a' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
                  <AlertCircle size={20} style={{ color: '#d97706' }} />
                  <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#92400e', margin: 0 }}>
                    Important Profile Information Missing from Resume
                  </h3>
                </div>
                <ul style={{ margin: 0, paddingLeft: '1.25rem', color: '#78350f', fontSize: '0.85rem', lineHeight: '1.7' }}>
                  {resumeData.missing_profile_info.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Strengths & Improvements */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6" style={{ marginBottom: '2rem' }}>
              
              {/* Strengths */}
              <div className="card">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                  <CheckCircle2 size={18} style={{ color: '#16a34a' }} />
                  <h3 style={{ fontSize: '1rem', fontWeight: 700, margin: 0 }}>Detected Resume Strengths</h3>
                </div>
                {resumeData.strengths && resumeData.strengths.length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {resumeData.strengths.map((str, idx) => (
                      <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem', fontSize: '0.85rem', color: '#334155' }}>
                        <span style={{ color: '#16a34a', fontWeight: 700 }}>✓</span>
                        <span>{str}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p style={{ color: '#64748b', fontSize: '0.85rem' }}>No specific strengths highlighted.</p>
                )}
              </div>

              {/* Improvements */}
              <div className="card">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                  <Zap size={18} style={{ color: '#ea580c' }} />
                  <h3 style={{ fontSize: '1rem', fontWeight: 700, margin: 0 }}>Recommended Action Items</h3>
                </div>
                {resumeData.improvements_suggested && resumeData.improvements_suggested.length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {resumeData.improvements_suggested.map((imp, idx) => (
                      <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem', fontSize: '0.85rem', color: '#334155' }}>
                        <span style={{ color: '#ea580c', fontWeight: 700 }}>•</span>
                        <span>{imp}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p style={{ color: '#64748b', fontSize: '0.85rem' }}>Your resume looks complete!</p>
                )}
              </div>

            </div>

            {/* Extracted Structured Sections (Tabs) */}
            <div className="card">
              
              {/* Tab Navigation Header */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.75rem', marginBottom: '1.5rem' }}>
                <button
                  type="button"
                  onClick={() => setActiveTab('overview')}
                  className={`btn ${activeTab === 'overview' ? 'btn-primary' : 'btn-secondary'}`}
                  style={{ padding: '0.45rem 1rem', fontSize: '0.825rem' }}
                >
                  <Code size={15} />
                  Skills ({((resumeData.technical_skills || []).length + (resumeData.programming_languages || []).length)})
                </button>

                <button
                  type="button"
                  onClick={() => setActiveTab('education')}
                  className={`btn ${activeTab === 'education' ? 'btn-primary' : 'btn-secondary'}`}
                  style={{ padding: '0.45rem 1rem', fontSize: '0.825rem' }}
                >
                  <GraduationCap size={15} />
                  Education ({(resumeData.education || []).length})
                </button>

                <button
                  type="button"
                  onClick={() => setActiveTab('projects')}
                  className={`btn ${activeTab === 'projects' ? 'btn-primary' : 'btn-secondary'}`}
                  style={{ padding: '0.45rem 1rem', fontSize: '0.825rem' }}
                >
                  <FileText size={15} />
                  Projects ({(resumeData.projects || []).length})
                </button>

                <button
                  type="button"
                  onClick={() => setActiveTab('experience')}
                  className={`btn ${activeTab === 'experience' ? 'btn-primary' : 'btn-secondary'}`}
                  style={{ padding: '0.45rem 1rem', fontSize: '0.825rem' }}
                >
                  <Briefcase size={15} />
                  Internships & Exp ({((resumeData.internships || []).length + (resumeData.experience || []).length)})
                </button>

                <button
                  type="button"
                  onClick={() => setActiveTab('certifications')}
                  className={`btn ${activeTab === 'certifications' ? 'btn-primary' : 'btn-secondary'}`}
                  style={{ padding: '0.45rem 1rem', fontSize: '0.825rem' }}
                >
                  <Award size={15} />
                  Certifications ({(resumeData.certifications || []).length})
                </button>
              </div>

              {/* Tab 1: Skills */}
              {activeTab === 'overview' && (
                <div>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#334155', marginBottom: '0.6rem' }}>
                    Programming Languages
                  </h4>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.45rem', marginBottom: '1.5rem' }}>
                    {resumeData.programming_languages && resumeData.programming_languages.length > 0 ? (
                      resumeData.programming_languages.map((lang, idx) => (
                        <span key={idx} className="badge badge-purple" style={{ fontSize: '0.825rem', padding: '0.35rem 0.75rem' }}>
                          {lang}
                        </span>
                      ))
                    ) : (
                      <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>No programming languages detected.</span>
                    )}
                  </div>

                  <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#334155', marginBottom: '0.6rem' }}>
                    Technical Skills & Frameworks
                  </h4>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.45rem', marginBottom: '1.5rem' }}>
                    {resumeData.technical_skills && resumeData.technical_skills.length > 0 ? (
                      resumeData.technical_skills.map((skill, idx) => (
                        <span key={idx} className="badge badge-blue" style={{ fontSize: '0.825rem', padding: '0.35rem 0.75rem' }}>
                          {skill}
                        </span>
                      ))
                    ) : (
                      <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>No technical skills detected.</span>
                    )}
                  </div>

                  {resumeData.soft_skills && resumeData.soft_skills.length > 0 && (
                    <>
                      <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#334155', marginBottom: '0.6rem' }}>
                        Soft Skills & Competencies
                      </h4>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.45rem' }}>
                        {resumeData.soft_skills.map((skill, idx) => (
                          <span key={idx} className="badge" style={{ background: '#f1f5f9', color: '#475569', fontSize: '0.825rem', padding: '0.35rem 0.75rem' }}>
                            {skill}
                          </span>
                        ))}
                      </div>
                    </>
                  )}
                </div>
              )}

              {/* Tab 2: Education */}
              {activeTab === 'education' && (
                <div>
                  {resumeData.education && resumeData.education.length > 0 ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                      {resumeData.education.map((edu, idx) => (
                        <div key={idx} style={{ padding: '1rem', background: '#f8fafc', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                            <span style={{ fontWeight: 700, fontSize: '0.95rem', color: '#0f172a' }}>
                              {edu.degree} {edu.branch && edu.branch !== 'Not specified' ? `— ${edu.branch}` : ''}
                            </span>
                            {edu.year && (
                              <span className="badge badge-blue">Year: {edu.year}</span>
                            )}
                          </div>
                          {edu.context && (
                            <p style={{ fontSize: '0.8rem', color: '#64748b', margin: 0 }}>
                              {edu.context}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>No education entries extracted.</p>
                  )}
                </div>
              )}

              {/* Tab 3: Projects */}
              {activeTab === 'projects' && (
                <div>
                  {resumeData.projects && resumeData.projects.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {resumeData.projects.map((proj, idx) => (
                        <div key={idx} style={{ padding: '1.25rem', background: '#f8fafc', borderRadius: '10px', border: '1px solid #e2e8f0', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                          <div>
                            <h4 style={{ fontWeight: 700, fontSize: '0.95rem', color: '#0f172a', marginBottom: '0.4rem' }}>
                              {proj.title}
                            </h4>
                            {proj.description && (
                              <p style={{ fontSize: '0.825rem', color: '#64748b', lineHeight: '1.5', marginBottom: '0.75rem' }}>
                                {proj.description}
                              </p>
                            )}
                          </div>

                          {proj.tech_stack && proj.tech_stack.length > 0 && (
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                              {proj.tech_stack.map((t, ti) => (
                                <span key={ti} className="badge badge-blue" style={{ fontSize: '0.75rem' }}>
                                  {t}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>No projects identified in resume text.</p>
                  )}
                </div>
              )}

              {/* Tab 4: Internships & Experience */}
              {activeTab === 'experience' && (
                <div>
                  {((resumeData.internships || []).length > 0 || (resumeData.experience || []).length > 0) ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                      {/* Internships */}
                      {(resumeData.internships || []).map((exp, idx) => (
                        <div key={`intern-${idx}`} style={{ padding: '1rem', background: '#f8fafc', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div>
                              <span style={{ fontWeight: 700, fontSize: '0.95rem', color: '#0f172a' }}>{exp.role}</span>
                              <span style={{ color: '#64748b', fontSize: '0.9rem' }}> at {exp.company}</span>
                            </div>
                            <span className="badge badge-green">Internship</span>
                          </div>
                          {exp.duration && (
                            <span style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '0.25rem', display: 'inline-block' }}>
                              Duration: {exp.duration}
                            </span>
                          )}
                        </div>
                      ))}

                      {/* Professional Experience */}
                      {(resumeData.experience || []).map((exp, idx) => (
                        <div key={`exp-${idx}`} style={{ padding: '1rem', background: '#f8fafc', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div>
                              <span style={{ fontWeight: 700, fontSize: '0.95rem', color: '#0f172a' }}>{exp.role}</span>
                              <span style={{ color: '#64748b', fontSize: '0.9rem' }}> at {exp.company}</span>
                            </div>
                            <span className="badge badge-blue">Experience</span>
                          </div>
                          {exp.duration && (
                            <span style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '0.25rem', display: 'inline-block' }}>
                              Duration: {exp.duration}
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>No internship or experience sections detected.</p>
                  )}
                </div>
              )}

              {/* Tab 5: Certifications */}
              {activeTab === 'certifications' && (
                <div>
                  {resumeData.certifications && resumeData.certifications.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {resumeData.certifications.map((cert, idx) => (
                        <div key={idx} style={{ padding: '1rem', background: '#f8fafc', borderRadius: '10px', border: '1px solid #e2e8f0', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                          <span style={{ fontWeight: 600, fontSize: '0.9rem', color: '#0f172a' }}>
                            {cert.title}
                          </span>
                          <span className="badge badge-purple">
                            {cert.issuer || 'Certified'}
                          </span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>No certifications detected in the resume text.</p>
                  )}
                </div>
              )}

            </div>

            {/* Next Step CTA */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1.5rem' }}>
              <button
                onClick={() => navigate('/companies-jobs')}
                className="btn btn-primary"
                style={{ padding: '0.75rem 1.5rem', fontSize: '0.9rem' }}
              >
                Proceed to Companies & Jobs
                <ArrowRight size={16} />
              </button>
            </div>

          </div>
        )}

      </div>
    </div>
  );
}
