import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import ActiveTargetIndicator from '../components/ActiveTargetIndicator';
import { useCareerTarget } from '../context/CareerTargetContext';
import { companyAPI, jobAPI, authAPI } from '../services/api';
import {
  Building2, Briefcase, Search, CheckCircle2, ArrowRight,
  ExternalLink, Sparkles, User, FileText, Target, Award,
  ShieldCheck, Loader2, LogOut, ChevronRight, AlertCircle,
  GraduationCap, Layers, Zap
} from 'lucide-react';

export default function CompanyJobs() {
  const navigate = useNavigate();
  const { activeTarget, setTargetJob } = useCareerTarget();

  const [loading, setLoading] = useState(true);
  const [companies, setCompanies] = useState([]);
  const [allCompaniesList, setAllCompaniesList] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [search, setSearch] = useState('');
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [selectedJob, setSelectedJob] = useState(null);
  const [settingTarget, setSettingTarget] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const [comps, allJobs] = await Promise.all([
        companyAPI.getCompanies(''),
        jobAPI.getJobs()
      ]);
      setCompanies(comps);
      setAllCompaniesList(comps);
      setJobs(allJobs);

      // Default select first company and job if available
      if (comps.length > 0) {
        setSelectedCompany(comps[0]);
        const companyJobs = allJobs.filter(j => j.company_id === comps[0].id);
        if (companyJobs.length > 0) {
          const jobDetail = await jobAPI.getJob(companyJobs[0].id);
          setSelectedJob(jobDetail);
        }
      }
    } catch (err) {
      setErrorMsg(err.message || 'Failed to load companies and job listings.');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    if (e && e.preventDefault) e.preventDefault();
    const query = search.trim().toLowerCase();
    if (!query) {
      setCompanies(allCompaniesList);
      if (allCompaniesList.length > 0 && (!selectedCompany || !allCompaniesList.some(c => c.id === selectedCompany.id))) {
        handleSelectCompany(allCompaniesList[0]);
      }
      return;
    }

    try {
      // Filter both client-side by company name, industry, and matching job titles/skills, and backend search
      const serverComps = await companyAPI.getCompanies(query).catch(() => []);
      const matchedCompIds = new Set(serverComps.map(c => c.id));

      allCompaniesList.forEach(c => {
        if (c.name.toLowerCase().includes(query) || c.industry.toLowerCase().includes(query)) {
          matchedCompIds.add(c.id);
        }
      });

      // Also match companies having jobs with matching title, domain, or skills
      jobs.forEach(j => {
        const titleMatch = j.title.toLowerCase().includes(query);
        const domainMatch = j.domain && j.domain.toLowerCase().includes(query);
        const skillMatch = j.skills && j.skills.some(s => s.toLowerCase().includes(query));
        if (titleMatch || domainMatch || skillMatch) {
          matchedCompIds.add(j.company_id);
        }
      });

      const filtered = allCompaniesList.filter(c => matchedCompIds.has(c.id));
      setCompanies(filtered);
      if (filtered.length > 0) {
        handleSelectCompany(filtered[0]);
      } else {
        setSelectedCompany(null);
        setSelectedJob(null);
      }
    } catch (err) {
      setErrorMsg(err.message || 'Search failed.');
    }
  };

  const handleClearSearch = () => {
    setSearch('');
    setCompanies(allCompaniesList);
    if (allCompaniesList.length > 0) {
      handleSelectCompany(allCompaniesList[0]);
    }
  };

  const handleSelectCompany = async (company) => {
    setSelectedCompany(company);
    const companyJobs = jobs.filter(j => j.company_id === company.id);
    if (companyJobs.length > 0) {
      const jobDetail = await jobAPI.getJob(companyJobs[0].id);
      setSelectedJob(jobDetail);
    } else {
      setSelectedJob(null);
    }
  };

  const handleSelectJob = async (jobId) => {
    try {
      const jobDetail = await jobAPI.getJob(jobId);
      setSelectedJob(jobDetail);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to load job requirements.');
    }
  };

  const handleSetTarget = async (jobId) => {
    setSettingTarget(true);
    setSuccessMsg('');
    setErrorMsg('');
    try {
      const updated = await setTargetJob(jobId, selectedCompany?.id);
      const title = updated?.job_title || selectedJob?.title || 'role';
      const company = updated?.company_name || selectedCompany?.name || 'company';
      setSuccessMsg(`Successfully set active target to ${title} at ${company}! All modules updated automatically.`);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to set target job.');
    } finally {
      setSettingTarget(false);
    }
  };

  const handleLogout = async () => {
    await authAPI.logout();
    navigate('/login');
  };

  const filteredJobs = selectedCompany
    ? jobs.filter(j => j.company_id === selectedCompany.id)
    : jobs;

  return (
    <div className="min-h-screen" style={{ paddingBottom: '3rem' }}>
      
      {/* Universal Top Navbar */}
      <Navbar />

      {/* Main Container */}
      <div className="container" style={{ marginTop: '1.5rem' }}>
        
        {/* Simple Page Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
          <div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 0.25rem 0' }}>
              Companies & Jobs
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', margin: 0 }}>
              Browse recruiting companies, explore open roles, and set your target position.
            </p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', alignItems: 'flex-end' }}>
            <ActiveTargetIndicator />
            {activeTarget && activeTarget.package_min_lpa && (
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textAlign: 'right' }}>
                Target CTC: {activeTarget.package_min_lpa} - {activeTarget.package_max_lpa} LPA
              </div>
            )}
          </div>
        </div>

        {/* Global Notifications */}
        {errorMsg && (
          <div className="alert alert-error" style={{ marginBottom: '1.25rem' }}>
            <AlertCircle size={18} />
            <span>{errorMsg}</span>
          </div>
        )}

        {successMsg && (
          <div className="alert alert-success" style={{ marginBottom: '1.25rem' }}>
            <CheckCircle2 size={18} />
            <span>{successMsg}</span>
          </div>
        )}

        {/* Search Bar across Companies, Jobs, and Skills */}
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem', width: '100%', alignItems: 'center', overflow: 'visible' }}>
          <div style={{ position: 'relative', flex: 1, minWidth: 0 }}>
            <Search size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-dim)', pointerEvents: 'none' }} />
            <input
              type="text"
              placeholder="Search companies, job roles, or required skills (e.g. Google, Cloud, React, Python)..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
              }}
              className="form-input"
              style={{ paddingLeft: '2.75rem', width: '100%' }}
            />
          </div>
          <button type="submit" className="btn btn-primary" style={{ padding: '0.65rem 1.5rem', flexShrink: 0, whiteSpace: 'nowrap', height: '42px' }}>
            Search
          </button>
          {search && (
            <button
              type="button"
              onClick={handleClearSearch}
              className="btn btn-secondary"
              style={{ padding: '0.65rem 1rem', flexShrink: 0, height: '42px' }}
            >
              Reset
            </button>
          )}
        </form>

        {loading ? (
          <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
            <Loader2 size={32} className="animate-spin" style={{ color: 'var(--primary)', margin: '0 auto 1rem' }} />
            <p style={{ color: 'var(--text-muted)' }}>Loading companies and jobs...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            {/* Column 1: Company List */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Building2 size={18} style={{ color: 'var(--text-muted)' }} />
                <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', margin: 0 }}>
                  Companies ({companies.length})
                </h3>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', maxHeight: '680px', overflowY: 'auto' }}>
                {companies.map((comp) => {
                  const isSelected = selectedCompany && selectedCompany.id === comp.id;
                  return (
                    <div
                      key={comp.id}
                      onClick={() => handleSelectCompany(comp)}
                      style={{
                        padding: '1rem',
                        background: isSelected ? 'var(--primary-light)' : 'var(--bg-card)',
                        border: `1.5px solid ${isSelected ? 'var(--primary)' : 'var(--border)'}`,
                        borderRadius: '12px',
                        cursor: 'pointer',
                        transition: 'all 0.15s ease'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                        <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-main)' }}>
                          {comp.name}
                        </h4>
                        <span className="badge badge-blue" style={{ fontSize: '0.7rem' }}>
                          {comp.tier}
                        </span>
                      </div>
                      <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: '0 0 0.5rem 0' }}>
                        {comp.industry} • {comp.location || 'Pan-India'}
                      </p>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                        <span>{comp.active_jobs_count} Available Role(s)</span>
                        <ChevronRight size={14} style={{ color: isSelected ? 'var(--primary)' : 'var(--border)' }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Column 2: Job Roles for Selected Company */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Briefcase size={18} style={{ color: 'var(--text-muted)' }} />
                <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', margin: 0 }}>
                  Available Job Roles ({filteredJobs.length})
                </h3>
              </div>

              {filteredJobs.length === 0 ? (
                <div className="card" style={{ textAlign: 'center', padding: '2rem' }}>
                  <Briefcase size={24} style={{ color: 'var(--text-dim)', margin: '0 auto 0.5rem' }} />
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No open roles listed for this company.</p>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', maxHeight: '680px', overflowY: 'auto', paddingTop: '10px' }}>
                  {filteredJobs.map((j) => {
                    const isSelected = selectedJob && selectedJob.id === j.id;
                    const isTarget = activeTarget && (activeTarget.job_id === j.id || activeTarget.id === j.id);
                    return (
                      <div
                        key={j.id}
                        onClick={() => handleSelectJob(j.id)}
                        style={{
                          padding: '1rem',
                          background: isSelected ? 'var(--primary-light)' : 'var(--bg-card)',
                          border: `1.5px solid ${isTarget ? '#10b981' : isSelected ? 'var(--primary)' : 'var(--border)'}`,
                          borderRadius: '12px',
                          cursor: 'pointer',
                          transition: 'all 0.15s ease',
                          position: 'relative'
                        }}
                      >
                        {isTarget && (
                          <span style={{
                            position: 'absolute',
                            top: '10px',
                            right: '10px',
                            background: '#10b981',
                            color: '#ffffff',
                            fontSize: '0.65rem',
                            fontWeight: 700,
                            padding: '0.15rem 0.55rem',
                            borderRadius: '999px',
                            boxShadow: '0 2px 4px rgba(0,0,0,0.15)'
                          }}>
                            Target Job
                          </span>
                        )}

                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '0.25rem', paddingRight: isTarget ? '75px' : '0' }}>
                          <h4 style={{ margin: 0, fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)' }}>
                            {j.title}
                          </h4>
                        </div>
                        <p style={{ fontSize: '0.775rem', color: 'var(--text-muted)', margin: '0 0 0.4rem 0' }}>
                          Domain: {j.domain} • {j.location}
                        </p>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontWeight: 700, color: '#16a34a', fontSize: '0.825rem' }}>
                            {j.package_min_lpa} - {j.package_max_lpa} LPA
                          </span>
                          <span style={{ fontSize: '0.75rem', color: 'var(--primary)', fontWeight: 600 }}>
                            View Details →
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Column 3: Full Job Details & Eligibility Criteria */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Target size={18} style={{ color: 'var(--text-muted)' }} />
                <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', margin: 0 }}>
                  Job Requirements
                </h3>
              </div>

              {selectedJob ? (
                <div className="card" style={{ position: 'sticky', top: '5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem', borderBottom: '1px solid var(--border)', paddingBottom: '0.75rem' }}>
                    <div>
                      <span className="badge badge-purple" style={{ fontSize: '0.7rem', marginBottom: '0.35rem' }}>
                        {selectedJob.company_name}
                      </span>
                      <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-main)', margin: '0 0 0.25rem 0' }}>
                        {selectedJob.title}
                      </h3>
                      <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', margin: 0 }}>
                        {selectedJob.location} • {selectedJob.role_type}
                      </p>
                    </div>

                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '1.25rem', fontWeight: 900, color: '#16a34a' }}>
                        {selectedJob.package_min_lpa} - {selectedJob.package_max_lpa} LPA
                      </div>
                      <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Expected CTC</span>
                    </div>
                  </div>

                  {/* Description */}
                  <p style={{ fontSize: '0.825rem', color: 'var(--text-main)', lineHeight: '1.6', marginBottom: '1.25rem' }}>
                    {selectedJob.description}
                  </p>

                  {/* Requirements Section */}
                  {selectedJob.requirement && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1.5rem' }}>
                      
                      {/* Must-Have Skills */}
                      <div>
                        <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#ef4444', textTransform: 'uppercase', display: 'block', marginBottom: '0.4rem' }}>
                          Must-Have Skills
                        </span>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                          {selectedJob.requirement.must_have_skills.map((skill, i) => (
                            <span key={i} className="badge badge-blue" style={{ fontSize: '0.75rem' }}>
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Good-To-Have Skills */}
                      {selectedJob.requirement.good_to_have_skills && (
                        <div>
                          <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#f59e0b', textTransform: 'uppercase', display: 'block', marginBottom: '0.4rem' }}>
                            Preferred / Bonus Skills
                          </span>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                            {selectedJob.requirement.good_to_have_skills.map((skill, i) => (
                              <span key={i} className="badge badge-purple" style={{ fontSize: '0.75rem' }}>
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Eligibility Metrics Grid */}
                      <div style={{ background: 'var(--bg-subtle)', padding: '0.85rem', borderRadius: '10px', border: '1px solid var(--border)', fontSize: '0.8rem' }}>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.5rem' }}>
                          <div>
                            <span style={{ color: 'var(--text-muted)' }}>Min CGPA: </span>
                            <strong style={{ color: 'var(--text-main)' }}>{selectedJob.requirement.min_cgpa}</strong>
                          </div>
                          <div>
                            <span style={{ color: 'var(--text-muted)' }}>Max Backlogs: </span>
                            <strong style={{ color: 'var(--text-main)' }}>{selectedJob.requirement.max_active_backlogs}</strong>
                          </div>
                          <div>
                            <span style={{ color: 'var(--text-muted)' }}>Min Projects: </span>
                            <strong style={{ color: 'var(--text-main)' }}>{selectedJob.requirement.min_projects_count}</strong>
                          </div>
                          <div>
                            <span style={{ color: 'var(--text-muted)' }}>Min Internships: </span>
                            <strong style={{ color: 'var(--text-main)' }}>{selectedJob.requirement.min_internships_count}</strong>
                          </div>
                        </div>

                        {selectedJob.requirement.eligible_branches && (
                          <div style={{ marginTop: '0.5rem', borderTop: '1px solid var(--border)', paddingTop: '0.4rem' }}>
                            <span style={{ color: 'var(--text-muted)' }}>Eligible Branches: </span>
                            <strong style={{ color: 'var(--text-main)' }}>{selectedJob.requirement.eligible_branches.join(', ')}</strong>
                          </div>
                        )}
                      </div>

                    </div>
                  )}

                  {/* Action Buttons */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                    <button
                      onClick={() => handleSetTarget(selectedJob.id)}
                      disabled={settingTarget || Boolean(activeTarget && (activeTarget.job_id === selectedJob.id || activeTarget.id === selectedJob.id))}
                      className="btn btn-primary"
                      style={{
                        width: '100%',
                        padding: '0.7rem',
                        background: (activeTarget && (activeTarget.job_id === selectedJob.id || activeTarget.id === selectedJob.id))
                          ? 'linear-gradient(135deg, #10b981, #059669)'
                          : undefined
                      }}
                    >
                      {settingTarget ? (
                        <>
                          <Loader2 size={16} className="animate-spin" />
                          Setting Target...
                        </>
                      ) : (activeTarget && (activeTarget.job_id === selectedJob.id || activeTarget.id === selectedJob.id)) ? (
                        <>
                          <CheckCircle2 size={16} />
                          Active Target Job
                        </>
                      ) : (
                        <>
                          <Target size={16} />
                          Set as Target Job
                        </>
                      )}
                    </button>

                    <button
                      onClick={() => navigate('/skill-gap')}
                      className="btn btn-secondary"
                      style={{ width: '100%', padding: '0.65rem' }}
                    >
                      Proceed to Skill Gap Analysis
                      <ArrowRight size={15} />
                    </button>
                  </div>

                </div>
              ) : (
                <div className="card" style={{ textAlign: 'center', padding: '3rem 1.5rem' }}>
                  <Target size={32} style={{ color: 'var(--text-dim)', margin: '0 auto 0.75rem' }} />
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                    Select a job role from the list to view eligibility requirements and set your target.
                  </p>
                </div>
              )}
            </div>

          </div>
        )}

      </div>
    </div>
  );
}
