import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import ActiveTargetIndicator from '../components/ActiveTargetIndicator';
import { useCareerTarget } from '../context/CareerTargetContext';
import { recommendationAPI, authAPI } from '../services/api';
import {
  Zap, CheckCircle2, AlertCircle, ArrowRight, ExternalLink,
  BookOpen, Code, Award, Briefcase, Sparkles, User, FileText,
  Building2, Layers, ShieldCheck, Target, Loader2, LogOut,
  RefreshCw, Check, CheckSquare, Square
} from 'lucide-react';

export default function CareerRecommendations() {
  const navigate = useNavigate();
  const { activeTarget, targetVersion } = useCareerTarget();

  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [data, setData] = useState(null);
  const [activeTab, setActiveTab] = useState('all'); // 'all' | 'skill' | 'course' | 'project' | 'certification' | 'coding' | 'aptitude' | 'interview'
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const currentTargetId = useRef(null);

  // Auto-refresh recommendations whenever active target changes
  useEffect(() => {
    const targetId = activeTarget?.job_id || activeTarget?.id;
    if (targetId && targetId !== currentTargetId.current) {
      currentTargetId.current = targetId;
      fetchRecommendations();
    }
  }, [activeTarget, targetVersion]);

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const res = await recommendationAPI.getRecommendations();
      setData(res);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to load career recommendations.');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateFresh = async () => {
    setGenerating(true);
    setErrorMsg('');
    setSuccessMsg('');
    try {
      const res = await recommendationAPI.generateRecommendations(true);
      setData(res);
      setSuccessMsg('Personalized career recommendations synthesized!');
    } catch (err) {
      setErrorMsg(err.message || 'Failed to generate recommendations.');
    } finally {
      setGenerating(false);
    }
  };

  const handleToggleComplete = async (recId, currentStatus) => {
    try {
      await recommendationAPI.toggleComplete(recId, !currentStatus);
      // Update local state
      setData(prev => {
        if (!prev) return prev;
        const updatedByCategory = { ...prev.by_category };
        for (const cat in updatedByCategory) {
          updatedByCategory[cat] = updatedByCategory[cat].map(item =>
            item.id === recId ? { ...item, is_completed: !currentStatus } : item
          );
        }
        return { ...prev, by_category: updatedByCategory };
      });
    } catch (err) {
      setErrorMsg('Failed to update task status.');
    }
  };

  const handleLogout = async () => {
    await authAPI.logout();
    navigate('/login');
  };

  // Flatten items for 'all' tab
  const allItems = data?.by_category
    ? Object.values(data.by_category).flat()
    : [];

  const displayItems = activeTab === 'all'
    ? allItems
    : (data?.by_category?.[activeTab] || []);

  const categoryIcons = {
    skill: <Target size={16} />,
    course: <BookOpen size={16} />,
    project: <Briefcase size={16} />,
    certification: <Award size={16} />,
    coding: <Code size={16} />,
    aptitude: <Zap size={16} />,
    interview: <User size={16} />
  };

  const getResourceUrl = (item) => {
    let url = item.action_url;
    if (!url || url.includes('devdocs.io') || url === 'https://github.com/' || url === 'https://github.com' || url.includes('pramp.com')) {
      const titleLower = (item.title || '').toLowerCase();
      const firstSkill = (item.mapped_skills && item.mapped_skills[0]) ? item.mapped_skills[0].toLowerCase() : '';
      
      if (item.type === 'skill') {
        if (firstSkill.includes('fastapi') || titleLower.includes('fastapi')) return 'https://fastapi.tiangolo.com/tutorial/';
        if (firstSkill.includes('react') || titleLower.includes('react')) return 'https://react.dev/learn';
        if (firstSkill.includes('docker') || titleLower.includes('docker')) return 'https://docs.docker.com/get-started/';
        if (firstSkill.includes('python') || titleLower.includes('python')) return 'https://docs.python.org/3/tutorial/';
        if (firstSkill.includes('sql') || firstSkill.includes('postgres') || titleLower.includes('postgres')) return 'https://www.postgresql.org/docs/current/tutorial.html';
        if (firstSkill.includes('aws') || titleLower.includes('aws')) return 'https://aws.amazon.com/getting-started/hands-on/';
        if (firstSkill.includes('kubernetes') || titleLower.includes('kubernetes')) return 'https://kubernetes.io/docs/tutorials/kubernetes-basics/';
        return `https://www.geeksforgeeks.org/search/?q=${encodeURIComponent(item.mapped_skills?.[0] || item.title)}`;
      }

      if (item.type === 'project') {
        if (titleLower.includes('microservice') || titleLower.includes('caching')) {
          return 'https://github.com/practical-tutorials/project-based-learning#go';
        }
        return 'https://github.com/practical-tutorials/project-based-learning#web-development';
      }

      if (item.type === 'interview') {
        return 'https://www.techinterviewhandbook.org/';
      }

      if (item.type === 'aptitude') {
        return 'https://www.geeksforgeeks.org/aptitude-questions-and-answers/';
      }

      if (item.type === 'coding') {
        return 'https://neetcode.io/practice';
      }
    }
    return url || 'https://roadmap.sh';
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
              Career Recommendations
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', margin: 0 }}>
              Curated action items, courses, and certifications tailored to your target job ({activeTarget?.job_title || data?.target_job_title || 'Target Job'}).
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
            <ActiveTargetIndicator />
            <button
              onClick={handleGenerateFresh}
              disabled={generating}
              className="btn btn-secondary"
              style={{ fontSize: '0.85rem' }}
            >
              <RefreshCw size={14} className={generating ? 'animate-spin' : ''} />
              <span>{generating ? 'Generating...' : 'Refresh'}</span>
            </button>
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

        {/* Category Filter Tabs */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1.5rem' }}>
          <button
            onClick={() => setActiveTab('all')}
            className={`btn ${activeTab === 'all' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.8rem', padding: '0.4rem 0.9rem' }}
          >
            All Recommendations ({allItems.length})
          </button>
          <button
            onClick={() => setActiveTab('skill')}
            className={`btn ${activeTab === 'skill' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.8rem', padding: '0.4rem 0.9rem' }}
          >
            Skills to Learn ({(data?.by_category?.skill || []).length})
          </button>
          <button
            onClick={() => setActiveTab('course')}
            className={`btn ${activeTab === 'course' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.8rem', padding: '0.4rem 0.9rem' }}
          >
            Courses ({(data?.by_category?.course || []).length})
          </button>
          <button
            onClick={() => setActiveTab('project')}
            className={`btn ${activeTab === 'project' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.8rem', padding: '0.4rem 0.9rem' }}
          >
            Projects ({(data?.by_category?.project || []).length})
          </button>
          <button
            onClick={() => setActiveTab('certification')}
            className={`btn ${activeTab === 'certification' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.8rem', padding: '0.4rem 0.9rem' }}
          >
            Certifications ({(data?.by_category?.certification || []).length})
          </button>
          <button
            onClick={() => setActiveTab('coding')}
            className={`btn ${activeTab === 'coding' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.8rem', padding: '0.4rem 0.9rem' }}
          >
            Coding / DSA ({(data?.by_category?.coding || []).length})
          </button>
          <button
            onClick={() => setActiveTab('aptitude')}
            className={`btn ${activeTab === 'aptitude' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.8rem', padding: '0.4rem 0.9rem' }}
          >
            Aptitude ({(data?.by_category?.aptitude || []).length})
          </button>
          <button
            onClick={() => setActiveTab('interview')}
            className={`btn ${activeTab === 'interview' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.8rem', padding: '0.4rem 0.9rem' }}
          >
            Interview Prep ({(data?.by_category?.interview || []).length})
          </button>
        </div>

        {/* Recommendations List */}
        {loading ? (
          <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
            <Loader2 size={32} className="animate-spin" style={{ color: 'var(--primary)', margin: '0 auto 1rem' }} />
            <p style={{ color: 'var(--text-muted)' }}>Synthesizing personalized recommendations...</p>
          </div>
        ) : displayItems.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
            <Zap size={32} style={{ color: 'var(--text-dim)', margin: '0 auto 0.75rem' }} />
            <p style={{ color: 'var(--text-muted)' }}>No recommendations in this category yet.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            {displayItems.map((item, idx) => (
              <div
                key={item.id || idx}
                className="card"
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  flexWrap: 'wrap',
                  gap: '1rem',
                  opacity: item.is_completed ? 0.65 : 1,
                  borderLeft: `4px solid ${item.priority === 'High' ? '#dc2626' : item.priority === 'Medium' ? '#d97706' : 'var(--primary)'}`
                }}
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem', flex: 1, minWidth: '300px' }}>
                  <button
                    onClick={() => handleToggleComplete(item.id, item.is_completed)}
                    style={{ background: 'none', border: 'none', cursor: 'pointer', color: item.is_completed ? '#16a34a' : 'var(--text-dim)', marginTop: '0.2rem' }}
                    title={item.is_completed ? 'Mark Incomplete' : 'Mark Completed'}
                  >
                    {item.is_completed ? <CheckSquare size={22} /> : <Square size={22} />}
                  </button>

                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem', flexWrap: 'wrap' }}>
                      <span className="badge" style={{ background: 'var(--bg-subtle)', color: 'var(--text-muted)', border: '1px solid var(--border)', fontSize: '0.7rem', display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                        {categoryIcons[item.type] || <Zap size={12} />}
                        {item.type.toUpperCase()}
                      </span>
                      <span className={`badge ${item.priority === 'High' ? 'badge-danger' : item.priority === 'Medium' ? 'badge-amber' : 'badge-blue'}`} style={{ fontSize: '0.7rem' }}>
                        {item.priority} Priority
                      </span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        Relevance: {item.relevance_score}%
                      </span>
                    </div>

                    <h3 style={{
                      margin: '0 0 0.35rem 0',
                      fontSize: '1rem',
                      fontWeight: 700,
                      color: item.is_completed ? 'var(--text-dim)' : 'var(--text-main)',
                      textDecoration: item.is_completed ? 'line-through' : 'none'
                    }}>
                      {item.title}
                    </h3>

                    {item.description && (
                      <p style={{ margin: 0, fontSize: '0.825rem', color: 'var(--text-muted)', lineHeight: '1.5' }}>
                        {item.description}
                      </p>
                    )}

                    {item.mapped_skills && item.mapped_skills.length > 0 && (
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.3rem', marginTop: '0.5rem' }}>
                        {item.mapped_skills.map((s, si) => (
                          <span key={si} className="badge badge-purple" style={{ fontSize: '0.7rem' }}>
                            {s}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                {getResourceUrl(item) && (
                  <a
                    href={getResourceUrl(item)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-secondary"
                    style={{ fontSize: '0.75rem', padding: '0.45rem 0.9rem', gap: '0.35rem' }}
                  >
                    Open Resource <ExternalLink size={13} />
                  </a>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Next Step CTA */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '2rem' }}>
          <button
            onClick={() => navigate('/roadmap')}
            className="btn btn-primary"
            style={{ padding: '0.75rem 1.5rem', fontSize: '0.9rem' }}
          >
            Proceed to Personalized Career Roadmap
            <ArrowRight size={16} />
          </button>
        </div>

      </div>
    </div>
  );
}
