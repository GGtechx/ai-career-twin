import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import ActiveTargetIndicator from '../components/ActiveTargetIndicator';
import { useCareerTarget } from '../context/CareerTargetContext';
import { dashboardAPI } from '../services/api';
import {
  Target, Zap, Briefcase, FileText, ArrowRight,
  Loader2, AlertCircle
} from 'lucide-react';

export default function Dashboard() {
  const { activeTarget, targetVersion } = useCareerTarget();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboard();
  }, [targetVersion, activeTarget?.id, activeTarget?.job_id]);

  const loadDashboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const summary = await dashboardAPI.getSummary();
      setData(summary);
    } catch (err) {
      setError(err.message || 'Failed to load dashboard.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen">
        <Navbar />
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 'calc(100vh - 64px)' }}>
          <div style={{ textAlign: 'center' }}>
            <Loader2 size={32} className="animate-spin" style={{ color: 'var(--primary)', margin: '0 auto 16px' }} />
            <p style={{ color: 'var(--text-muted)', fontSize: '15px' }}>Loading dashboard...</p>
          </div>
        </div>
      </div>
    );
  }

  const { profile, resume, target_job, skill_gap, placement, roadmap, career_twin, top_action_items } = data || {};

  return (
    <div className="min-h-screen" style={{ paddingBottom: '3rem' }}>
      <Navbar />

      <div className="container" style={{ marginTop: '1.5rem' }}>
        {error && (
          <div className="alert alert-error" style={{ marginBottom: '1.25rem' }}>
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        {/* Profile Header */}
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
              <div style={{ width: '52px', height: '52px', borderRadius: '12px', background: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '22px', fontWeight: '800', color: '#fff' }}>
                {profile?.full_name ? profile.full_name.charAt(0).toUpperCase() : 'S'}
              </div>
              <div>
                <h1 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-main)' }}>
                  {profile?.full_name || 'Student'}
                </h1>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '2px' }}>
                  {profile?.degree || 'B.Tech'} in {profile?.branch || 'Computer Science'} • CGPA: <strong style={{ color: 'var(--text-main)' }}>{profile?.cgpa || 7.5}</strong> • {profile?.college_name || 'Engineering Institute'}
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', alignItems: 'center' }}>
              <ActiveTargetIndicator />
              <Link to="/career-twin" className="btn btn-primary" style={{ fontSize: '0.8rem', padding: '8px 14px' }}>
                View Career Twin
              </Link>
            </div>
          </div>
        </div>

        {/* Key Metrics */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
          {/* Career Target */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>Career Target</span>
              <Target size={18} style={{ color: 'var(--primary)' }} />
            </div>
            <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '8px' }}>
              {activeTarget?.job_title || target_job?.target_job_role || 'No Target Selected'}
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--primary)', fontWeight: 600, marginTop: '2px' }}>
              {activeTarget?.company_name || target_job?.target_company || 'Browse companies to pick a role'}
            </div>
            <Link to="/companies-jobs" style={{ display: 'inline-block', marginTop: '10px', fontSize: '0.75rem', color: 'var(--primary)', textDecoration: 'none', fontWeight: 600 }}>
              Manage Target Job →
            </Link>
          </div>

          {/* Skill Match */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>Skill Match</span>
              <Zap size={18} style={{ color: '#10b981' }} />
            </div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px', marginTop: '8px' }}>
              <span style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-main)' }}>
                {skill_gap?.match_percentage || 0}%
              </span>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>({skill_gap?.readiness_tier || 'Moderate'})</span>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
              {skill_gap?.matched_skills_count || 0} skills aligned with target
            </div>
            <Link to="/skill-gap" style={{ display: 'inline-block', marginTop: '10px', fontSize: '0.75rem', color: 'var(--primary)', textDecoration: 'none', fontWeight: 600 }}>
              View Gap Analysis →
            </Link>
          </div>

          {/* Placement Readiness */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>Placement Readiness</span>
              <Briefcase size={18} style={{ color: '#8b5cf6' }} />
            </div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px', marginTop: '8px' }}>
              <span style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-main)' }}>
                {placement?.readiness_score || 65}%
              </span>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{placement?.readiness_category}</span>
            </div>
            <div style={{ fontSize: '0.75rem', color: '#f59e0b', fontWeight: 600, marginTop: '4px' }}>
              Est. Package: {placement?.predicted_salary_min_lpa || 7.5} - {placement?.predicted_salary_max_lpa || 12.0} LPA
            </div>
            <Link to="/placement-readiness" style={{ display: 'inline-block', marginTop: '10px', fontSize: '0.75rem', color: 'var(--primary)', textDecoration: 'none', fontWeight: 600 }}>
              View Details →
            </Link>
          </div>

          {/* Resume ATS */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>Resume ATS Score</span>
              <FileText size={18} style={{ color: '#0ea5e9' }} />
            </div>
            {resume?.has_resume ? (
              <>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px', marginTop: '8px' }}>
                  <span style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-main)' }}>
                    {resume.ats_score}%
                  </span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>({resume.ats_rating})</span>
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {resume.file_name} • {resume.extracted_skills_count} skills extracted
                </div>
              </>
            ) : (
              <div style={{ marginTop: '8px', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                No resume analyzed yet.
              </div>
            )}
            <Link to="/resume-analysis" style={{ display: 'inline-block', marginTop: '10px', fontSize: '0.75rem', color: 'var(--primary)', textDecoration: 'none', fontWeight: 600 }}>
              Resume Analysis →
            </Link>
          </div>
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Skills & Gaps */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)' }}>
                Technical Skills & Gaps
              </h3>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                {profile?.technical_skills?.length || 0} skills
              </span>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700, marginBottom: '8px' }}>
                Current Skills
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {profile?.technical_skills && profile.technical_skills.length > 0 ? (
                  profile.technical_skills.map((s, i) => (
                    <span key={i} className="badge badge-blue">{s}</span>
                  ))
                ) : (
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>No skills added. Add in Profile.</span>
                )}
              </div>
            </div>

            {skill_gap?.missing_critical_skills && skill_gap.missing_critical_skills.length > 0 && (
              <div style={{ borderTop: '1px solid var(--border)', paddingTop: '12px' }}>
                <div style={{ fontSize: '0.7rem', color: '#ef4444', textTransform: 'uppercase', fontWeight: 700, marginBottom: '8px' }}>
                  Critical Gaps for {target_job?.target_job_role || 'Target Role'}
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                  {skill_gap.missing_critical_skills.map((gap, i) => (
                    <span key={i} className="badge badge-danger">{gap}</span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Career Roadmap Progress */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)' }}>
                  Roadmap Progress
                </h3>
                <div style={{ fontSize: '0.75rem', color: '#f59e0b', fontWeight: 600, marginTop: '2px' }}>
                  Current: {roadmap?.current_stage || 'Skill Foundation'}
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <span style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--primary)' }}>
                  {roadmap?.overall_progress_percentage || 0}%
                </span>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                  {roadmap?.completed_tasks || 0}/{roadmap?.total_tasks || 14} tasks
                </div>
              </div>
            </div>

            <div style={{ height: '8px', background: 'var(--border)', borderRadius: '4px', overflow: 'hidden', marginBottom: '12px' }}>
              <div style={{ height: '100%', width: `${roadmap?.overall_progress_percentage || 0}%`, background: 'var(--primary)', borderRadius: '4px', transition: 'width 0.5s ease-out' }} />
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                7 stages: foundation to mock interviews
              </span>
              <Link to="/roadmap" style={{ fontSize: '0.75rem', color: 'var(--primary)', textDecoration: 'none', fontWeight: 600 }}>
                Open Roadmap →
              </Link>
            </div>
          </div>

          {/* Career Twin Score */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)' }}>
                Career Twin Score
              </h3>
              <div style={{ textAlign: 'right' }}>
                <span style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-main)' }}>
                  {career_twin?.overall_twin_score || 64}
                </span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>/100</span>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {career_twin?.radar_breakdown &&
                Object.entries(career_twin.radar_breakdown).map(([dim, val]) => (
                  <div key={dim}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '3px' }}>
                      <span style={{ color: 'var(--text-main)' }}>{dim}</span>
                      <span style={{ fontWeight: 700, color: val >= 75 ? '#10b981' : val >= 60 ? '#f59e0b' : '#ef4444' }}>
                        {val}
                      </span>
                    </div>
                    <div style={{ height: '6px', background: 'var(--border)', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${Math.min(100, Math.max(0, val))}%`, background: val >= 75 ? '#10b981' : val >= 60 ? '#f59e0b' : '#ef4444', borderRadius: '3px' }} />
                    </div>
                  </div>
                ))}
            </div>

            <div style={{ marginTop: '12px', paddingTop: '10px', borderTop: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Simulate skill impacts</span>
              <Link to="/career-twin" style={{ fontSize: '0.75rem', color: 'var(--primary)', textDecoration: 'none', fontWeight: 700 }}>
                Launch Simulator →
              </Link>
            </div>
          </div>

          {/* Next Steps */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)' }}>
                Next Steps
              </h3>
              <Link to="/recommendations" style={{ fontSize: '0.75rem', color: 'var(--primary)', textDecoration: 'none', fontWeight: 600 }}>
                View All →
              </Link>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {top_action_items && top_action_items.length > 0 ? (
                top_action_items.map((item, idx) => (
                  <div key={idx} style={{ background: 'var(--bg-subtle)', border: '1px solid var(--border)', padding: '10px 12px', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)' }}>{item.title}</div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                        {item.category} • <span style={{ color: '#ef4444' }}>{item.priority}</span>
                      </div>
                    </div>
                    <Link to={item.action_url || '/recommendations'} className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: '0.7rem' }}>
                      Action →
                    </Link>
                  </div>
                ))
              ) : (
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', margin: 0 }}>All recommendations current.</p>
              )}
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @media (max-width: 900px) {
          .grid { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </div>
  );
}
