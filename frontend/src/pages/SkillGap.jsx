import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import ActiveTargetIndicator from '../components/ActiveTargetIndicator';
import { useCareerTarget } from '../context/CareerTargetContext';
import { skillGapAPI, jobAPI, authAPI } from '../services/api';
import {
  Layers, CheckCircle2, AlertTriangle, AlertCircle, ArrowRight,
  Target, Sparkles, User, FileText, Building2, ShieldCheck,
  Zap, Loader2, LogOut, RefreshCw, ChevronRight, HelpCircle
} from 'lucide-react';

export default function SkillGap() {
  const navigate = useNavigate();
  const { activeTarget, setTargetJob, targetVersion } = useCareerTarget();

  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const currentTargetId = useRef(null);

  // Sync selected job ID and auto-run when activeTarget changes
  useEffect(() => {
    const targetId = activeTarget?.job_id || activeTarget?.id;
    if (targetId && targetId !== currentTargetId.current) {
      currentTargetId.current = targetId;
      setSelectedJobId(targetId);
      handleRunAnalysis(targetId);
    }
  }, [activeTarget, targetVersion]);

  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const allJobs = await jobAPI.getJobs();
      setJobs(allJobs);

      const targetId = activeTarget?.job_id || activeTarget?.id;
      if (targetId) {
        setSelectedJobId(targetId);
        await handleRunAnalysis(targetId);
      } else {
        const latestAnalysis = await skillGapAPI.getMyLatestSkillGap().catch(() => null);
        if (latestAnalysis) {
          setAnalysisResult(latestAnalysis);
          setSelectedJobId(latestAnalysis.job_role_id);
        } else if (allJobs.length > 0) {
          setSelectedJobId(allJobs[0].id);
          await handleRunAnalysis(allJobs[0].id);
        }
      }
    } catch (err) {
      setErrorMsg(err.message || 'Failed to initialize skill gap analysis.');
    } finally {
      setLoading(false);
    }
  };

  const handleRunAnalysis = async (jobId) => {
    const targetId = jobId || selectedJobId;
    if (!targetId) {
      setErrorMsg('Please select a target job role.');
      return;
    }

    setAnalyzing(true);
    setErrorMsg('');
    setSuccessMsg('');
    try {
      const result = await skillGapAPI.analyzeSkillGap(targetId);
      setAnalysisResult(result);
      setSuccessMsg(`Skill gap evaluation completed for ${result.job_title} at ${result.company_name}!`);
    } catch (err) {
      setErrorMsg(err.message || 'Skill gap analysis failed.');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleLogout = async () => {
    await authAPI.logout();
    navigate('/login');
  };

  const getTierColor = (tier) => {
    if (tier === 'High Readiness') return { bg: '#dcfce7', text: '#15803d', bar: '#16a34a' };
    if (tier === 'Moderate Readiness') return { bg: '#fef3c7', text: '#b45309', bar: '#d97706' };
    return { bg: '#fee2e2', text: '#b91c1c', bar: '#dc2626' };
  };

  return (
    <div className="min-h-screen" style={{ paddingBottom: '4rem' }}>
      
      {/* Universal Top Navbar */}
      <Navbar />

      {/* Main Container */}
      <div className="container" style={{ marginTop: '1.5rem' }}>
        
        {/* Page Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
          <div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 0.25rem 0' }}>
              Skill Gap Analysis
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', margin: 0 }}>
              Compare your profile skills and resume against requirements for your target job position.
            </p>
          </div>
          <div>
            <ActiveTargetIndicator />
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

        {/* Job Selection Controls */}
        <div className="card" style={{ marginBottom: '1.75rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
            <div style={{ flex: 1, minWidth: '280px' }}>
              <label className="form-label">Active Career Target for Skill Gap Evaluation</label>
              <select
                value={selectedJobId}
                onChange={async (e) => {
                  const newJobId = parseInt(e.target.value);
                  setSelectedJobId(newJobId);
                  await setTargetJob(newJobId);
                }}
                className="form-select"
              >
                {jobs.map((j) => (
                  <option key={j.id} value={j.id}>
                    {j.title} — {j.company_name} ({j.domain})
                  </option>
                ))}
              </select>
            </div>

            <button
              onClick={() => handleRunAnalysis(selectedJobId)}
              disabled={analyzing}
              className="btn btn-primary"
              style={{ padding: '0.7rem 1.5rem', alignSelf: 'flex-end' }}
            >
              {analyzing ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  Evaluating Skill Gap...
                </>
              ) : (
                <>
                  <RefreshCw size={16} />
                  Refresh Analysis
                </>
              )}
            </button>
          </div>
        </div>

        {loading ? (
          <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
            <Loader2 size={32} className="animate-spin" style={{ color: 'var(--primary)', margin: '0 auto 1rem' }} />
            <p style={{ color: 'var(--text-muted)' }}>Analyzing skill alignment...</p>
          </div>
        ) : analysisResult ? (
          <div>
            
            {/* Top Match Score & Overview Banner */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6" style={{ marginBottom: '1.75rem' }}>
              
              {/* Match Score Card */}
              <div className="card" style={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                borderLeft: `5px solid ${getTierColor(analysisResult.readiness_tier).bar}`
              }}>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                    <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                      Skill Match Score
                    </span>
                    <span style={{
                      padding: '0.2rem 0.6rem',
                      borderRadius: '999px',
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      backgroundColor: getTierColor(analysisResult.readiness_tier).bg,
                      color: getTierColor(analysisResult.readiness_tier).text
                    }}>
                      {analysisResult.readiness_tier}
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem', marginBottom: '0.75rem' }}>
                    <span style={{ fontSize: '2.75rem', fontWeight: 900, color: 'var(--text-main)', lineHeight: 1 }}>
                      {analysisResult.match_percentage}%
                    </span>
                    <span style={{ fontSize: '1rem', color: 'var(--text-dim)' }}>Alignment</span>
                  </div>

                  <div style={{ width: '100%', height: '8px', background: 'var(--border)', borderRadius: '999px', overflow: 'hidden' }}>
                    <div style={{
                      width: `${analysisResult.match_percentage}%`,
                      height: '100%',
                      background: getTierColor(analysisResult.readiness_tier).bar,
                      borderRadius: '999px',
                      transition: 'width 0.6s ease'
                    }} />
                  </div>
                </div>

                <div style={{ marginTop: '1rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  Target: <strong>{analysisResult.job_title}</strong> at <strong>{analysisResult.company_name}</strong>
                </div>
              </div>

              {/* Matched vs Missing Summary */}
              <div className="card" style={{ gridColumn: 'span 2' }}>
                <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '1rem' }}>
                  Competency Distribution Summary
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4" style={{ textAlign: 'center' }}>
                  <div style={{ background: '#f0fdf4', padding: '1rem', borderRadius: '10px', border: '1px solid #bbf7d0' }}>
                    <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#16a34a' }}>
                      {analysisResult.matched_skills.length}
                    </div>
                    <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#15803d' }}>
                      Matched Competencies
                    </span>
                  </div>

                  <div style={{ background: '#fef2f2', padding: '1rem', borderRadius: '10px', border: '1px solid #fecaca' }}>
                    <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#dc2626' }}>
                      {analysisResult.missing_critical_skills.length}
                    </div>
                    <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#b91c1c' }}>
                      Critical Gaps (Must-Have)
                    </span>
                  </div>

                  <div style={{ background: '#fffbeb', padding: '1rem', borderRadius: '10px', border: '1px solid #fde68a' }}>
                    <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#d97706' }}>
                      {analysisResult.missing_secondary_skills.length}
                    </div>
                    <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#b45309' }}>
                      Secondary Gaps (Preferred)
                    </span>
                  </div>
                </div>

                {analysisResult.analysis_notes && (
                  <p style={{ marginTop: '1rem', fontSize: '0.8rem', color: 'var(--text-muted)', fontStyle: 'italic', margin: '1rem 0 0 0' }}>
                    {analysisResult.analysis_notes}
                  </p>
                )}
              </div>

            </div>

            {/* Matched Skills vs Missing Skills Details */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6" style={{ marginBottom: '1.75rem' }}>
              
              {/* Matched Skills */}
              <div className="card">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                  <CheckCircle2 size={20} style={{ color: '#16a34a' }} />
                  <h3 style={{ fontSize: '1rem', fontWeight: 700, margin: 0, color: 'var(--text-main)' }}>
                    Matched Skills ({analysisResult.matched_skills.length})
                  </h3>
                </div>
                {analysisResult.matched_skills.length > 0 ? (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                    {analysisResult.matched_skills.map((skill, i) => (
                      <span key={i} className="badge badge-green" style={{ fontSize: '0.8rem', padding: '0.35rem 0.75rem' }}>
                        ✓ {skill}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p style={{ color: 'var(--text-dim)', fontSize: '0.85rem' }}>No direct matching skills detected.</p>
                )}
              </div>

              {/* Missing Skills */}
              <div className="card">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                  <AlertTriangle size={20} style={{ color: '#dc2626' }} />
                  <h3 style={{ fontSize: '1rem', fontWeight: 700, margin: 0, color: 'var(--text-main)' }}>
                    Missing Skill Gaps ({(analysisResult.missing_critical_skills.length + analysisResult.missing_secondary_skills.length)})
                  </h3>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {analysisResult.missing_critical_skills.length > 0 && (
                    <div>
                      <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#dc2626', textTransform: 'uppercase', display: 'block', marginBottom: '0.35rem' }}>
                        Critical (Must-Have for Screening)
                      </span>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                        {analysisResult.missing_critical_skills.map((s, i) => (
                          <span key={i} className="badge badge-danger" style={{ fontSize: '0.8rem', padding: '0.35rem 0.75rem' }}>
                            ✕ {s}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {analysisResult.missing_secondary_skills.length > 0 && (
                    <div>
                      <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#d97706', textTransform: 'uppercase', display: 'block', marginBottom: '0.35rem' }}>
                        Preferred (Bonus Skills)
                      </span>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                        {analysisResult.missing_secondary_skills.map((s, i) => (
                          <span key={i} className="badge badge-amber" style={{ fontSize: '0.8rem', padding: '0.35rem 0.75rem' }}>
                            • {s}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>

            </div>

            {/* Priority Skill Gaps & Action Items */}
            {analysisResult.priority_skill_gaps && analysisResult.priority_skill_gaps.length > 0 && (
              <div className="card" style={{ marginBottom: '1.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                  <Target size={20} style={{ color: 'var(--primary)' }} />
                  <h3 style={{ fontSize: '1.05rem', fontWeight: 700, margin: 0, color: 'var(--text-main)' }}>
                    Priority Gap Learning Directives
                  </h3>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {analysisResult.priority_skill_gaps.map((item, idx) => (
                    <div key={idx} style={{
                      padding: '0.9rem',
                      background: item.priority === 'High Priority' ? 'rgba(239, 68, 68, 0.08)' : 'var(--bg-subtle)',
                      border: `1px solid ${item.priority === 'High Priority' ? 'rgba(239, 68, 68, 0.25)' : 'var(--border)'}`,
                      borderRadius: '10px',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      flexWrap: 'wrap',
                      gap: '0.75rem'
                    }}>
                      <div style={{ flex: 1, minWidth: '240px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.2rem' }}>
                          <strong style={{ color: 'var(--text-main)', fontSize: '0.95rem' }}>{item.skill}</strong>
                          <span className={`badge ${item.priority === 'High Priority' ? 'badge-danger' : 'badge-amber'}`} style={{ fontSize: '0.7rem' }}>
                            {item.priority}
                          </span>
                        </div>
                        <p style={{ margin: 0, fontSize: '0.825rem', color: 'var(--text-muted)' }}>
                          {item.recommendation}
                        </p>
                      </div>

                      <Link
                        to="/recommendations"
                        className="btn btn-secondary"
                        style={{ fontSize: '0.75rem', padding: '0.4rem 0.8rem' }}
                      >
                        Find Courses →
                      </Link>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Next Steps CTA */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
              <button
                onClick={() => navigate('/placement')}
                className="btn btn-primary"
                style={{ padding: '0.75rem 1.5rem', fontSize: '0.9rem' }}
              >
                Proceed to Placement Readiness Prediction
                <ArrowRight size={16} />
              </button>
            </div>

          </div>
        ) : null}

      </div>
    </div>
  );
}
