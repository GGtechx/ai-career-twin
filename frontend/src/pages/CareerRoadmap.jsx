import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import ActiveTargetIndicator from '../components/ActiveTargetIndicator';
import { useCareerTarget } from '../context/CareerTargetContext';
import { roadmapAPI, authAPI } from '../services/api';
import {
  Target, CheckCircle2, AlertCircle, ArrowRight, Check,
  Clock, Sparkles, User, FileText, Building2, Layers,
  ShieldCheck, Zap, Loader2, LogOut, RefreshCw, Calendar,
  ChevronDown, ChevronUp, Circle, CheckCircle
} from 'lucide-react';

export default function CareerRoadmap() {
  const navigate = useNavigate();
  const { activeTarget, targetVersion } = useCareerTarget();
  const [loading, setLoading] = useState(true);
  const [updatingTaskId, setUpdatingTaskId] = useState(null);
  const [roadmap, setRoadmap] = useState(null);
  const [expandedStages, setExpandedStages] = useState({ 1: true, 2: true, 3: true, 4: true, 5: true, 6: true, 7: true });
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  useEffect(() => {
    fetchRoadmap();
  }, [targetVersion, activeTarget?.id, activeTarget?.job_id]);

  const fetchRoadmap = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const data = await roadmapAPI.getRoadmap();
      setRoadmap(data);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to load career roadmap.');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleTaskStatus = async (item) => {
    const nextStatus = item.status === 'Completed' ? 'In Progress' : 'Completed';
    setUpdatingTaskId(item.item_id);
    setErrorMsg('');
    try {
      const updated = await roadmapAPI.updateTask(item.item_id, {
        status: nextStatus,
        completion_percentage: nextStatus === 'Completed' ? 100.0 : 50.0
      });
      setRoadmap(updated);
      setSuccessMsg(`Task "${item.title}" marked as ${nextStatus}!`);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to update task progress.');
    } finally {
      setUpdatingTaskId(null);
    }
  };

  const handleRegenerateRoadmap = async () => {
    setLoading(true);
    setErrorMsg('');
    setSuccessMsg('');
    try {
      const res = await roadmapAPI.generateRoadmap(true);
      setRoadmap(res);
      setSuccessMsg('Roadmap regenerated and aligned with latest placement goals!');
    } catch (err) {
      setErrorMsg(err.message || 'Failed to regenerate roadmap.');
    } finally {
      setLoading(false);
    }
  };

  const toggleStage = (stageNum) => {
    setExpandedStages(prev => ({ ...prev, [stageNum]: !prev[stageNum] }));
  };

  const handleLogout = async () => {
    await authAPI.logout();
    navigate('/login');
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
            <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0f172a', margin: '0 0 0.25rem 0' }}>
              Career Roadmap
            </h1>
            <p style={{ color: '#64748b', fontSize: '0.875rem', margin: 0 }}>
              Target: {activeTarget?.job_title || roadmap?.target_job_title || 'Software Engineer'} at {activeTarget?.company_name || roadmap?.target_company_name || 'Corporate'} • {roadmap?.target_timeline_weeks || 12} Weeks Schedule
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
            <ActiveTargetIndicator />
            <button
              onClick={handleRegenerateRoadmap}
              disabled={loading}
              className="btn btn-secondary"
              style={{ fontSize: '0.85rem' }}
            >
              <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
              <span>Refresh Roadmap</span>
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

        {loading ? (
          <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
            <Loader2 size={32} className="animate-spin" style={{ color: '#0d9488', margin: '0 auto 1rem' }} />
            <p style={{ color: '#64748b' }}>Generating personalized milestone progression...</p>
          </div>
        ) : roadmap ? (
          <div>
            
            {/* Overall Progress Dashboard */}
            <div className="card" style={{ marginBottom: '2rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1rem' }}>
                <div>
                  <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-main)', margin: '0 0 0.25rem 0' }}>
                    {roadmap.title}
                  </h3>
                  <span style={{ fontSize: '0.825rem', color: 'var(--text-muted)' }}>
                    Milestones Completed: <strong>{roadmap.completed_tasks}</strong> / {roadmap.total_tasks} Total Tasks
                  </span>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <span style={{ fontSize: '2rem', fontWeight: 900, color: '#0d9488' }}>
                    {roadmap.overall_progress_percentage}%
                  </span>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block' }}>Overall Completion</span>
                </div>
              </div>

              {/* Progress bar */}
              <div style={{ width: '100%', height: '10px', background: 'var(--border)', borderRadius: '999px', overflow: 'hidden' }}>
                <div style={{
                  width: `${roadmap.overall_progress_percentage}%`,
                  height: '100%',
                  background: 'linear-gradient(90deg, #0d9488, #14b8a6)',
                  borderRadius: '999px',
                  transition: 'width 0.6s ease'
                }} />
              </div>
            </div>

            {/* 7 Roadmap Stages */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              {roadmap.stages.map((stage) => {
                const isExpanded = expandedStages[stage.stage_number];
                return (
                  <div key={stage.stage_number} className="card" style={{ padding: '1.25rem 1.5rem' }}>
                    
                    {/* Stage Header */}
                    <div
                      onClick={() => toggleStage(stage.stage_number)}
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        cursor: 'pointer',
                        userSelect: 'none'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                        <div style={{
                          width: '32px',
                          height: '32px',
                          borderRadius: '50%',
                          background: stage.stage_progress_percentage === 100 ? '#10b981' : '#0f766e',
                          color: '#ffffff',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontWeight: 800,
                          fontSize: '0.85rem'
                        }}>
                          {stage.stage_progress_percentage === 100 ? <Check size={18} /> : stage.stage_number}
                        </div>

                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 800, color: 'var(--text-main)' }}>
                              Stage {stage.stage_number}: {stage.stage_name}
                            </h3>
                            {stage.stage_progress_percentage === 100 && (
                              <span className="badge badge-green" style={{ fontSize: '0.7rem' }}>
                                Completed
                              </span>
                            )}
                          </div>
                          <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                            {stage.description}
                          </p>
                        </div>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <div style={{ textAlign: 'right' }}>
                          <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#0f766e' }}>
                            {stage.stage_progress_percentage}%
                          </span>
                        </div>
                        {isExpanded ? <ChevronUp size={20} style={{ color: 'var(--text-muted)' }} /> : <ChevronDown size={20} style={{ color: 'var(--text-muted)' }} />}
                      </div>
                    </div>

                    {/* Stage Tasks List */}
                    {isExpanded && (
                      <div style={{ marginTop: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.75rem', borderTop: '1px solid var(--border)', paddingTop: '1rem' }}>
                        {stage.items.map((item) => {
                          const isDone = item.status === 'Completed';
                          const isUpdating = updatingTaskId === item.item_id;
                          return (
                            <div
                              key={item.item_id}
                              style={{
                                padding: '1rem',
                                background: isDone ? 'rgba(16, 185, 129, 0.1)' : 'var(--bg-subtle)',
                                border: `1px solid ${isDone ? 'rgba(16, 185, 129, 0.25)' : 'var(--border)'}`,
                                borderRadius: '10px',
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center',
                                flexWrap: 'wrap',
                                gap: '1rem'
                              }}
                            >
                              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem', flex: 1, minWidth: '260px' }}>
                                <button
                                  onClick={() => handleToggleTaskStatus(item)}
                                  disabled={isUpdating}
                                  style={{
                                    background: 'none',
                                    border: 'none',
                                    cursor: 'pointer',
                                    color: isDone ? '#10b981' : 'var(--text-dim)',
                                    marginTop: '0.15rem'
                                  }}
                                  title="Toggle status"
                                >
                                  {isDone ? <CheckCircle size={22} /> : <Circle size={22} />}
                                </button>

                                <div>
                                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.2rem', flexWrap: 'wrap' }}>
                                    <h4 style={{
                                      margin: 0,
                                      fontSize: '0.925rem',
                                      fontWeight: 700,
                                      color: isDone ? '#10b981' : 'var(--text-main)',
                                      textDecoration: isDone ? 'line-through' : 'none'
                                    }}>
                                      {item.title}
                                    </h4>
                                    <span className={`badge ${item.priority === 'High' ? 'badge-danger' : 'badge-amber'}`} style={{ fontSize: '0.65rem' }}>
                                      {item.priority}
                                    </span>
                                  </div>

                                  <p style={{ margin: 0, fontSize: '0.8rem', color: isDone ? 'var(--text-dim)' : 'var(--text-muted)', lineHeight: '1.5' }}>
                                    {item.description}
                                  </p>

                                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginTop: '0.4rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                                      <Clock size={12} /> {item.estimated_duration}
                                    </span>
                                    <span>Status: <strong>{item.status}</strong></span>
                                  </div>
                                </div>
                              </div>

                              <button
                                onClick={() => handleToggleTaskStatus(item)}
                                disabled={isUpdating}
                                className={`btn ${isDone ? 'btn-secondary' : 'btn-primary'}`}
                                style={{ padding: '0.4rem 0.85rem', fontSize: '0.75rem' }}
                              >
                                {isUpdating ? (
                                  <Loader2 size={14} className="animate-spin" />
                                ) : isDone ? (
                                  'Mark Incomplete'
                                ) : (
                                  'Mark Done ✓'
                                )}
                              </button>
                            </div>
                          );
                        })}
                      </div>
                    )}

                  </div>
                );
              })}
            </div>

          </div>
        ) : null}

      </div>
    </div>
  );
}
