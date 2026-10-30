import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import ActiveTargetIndicator from '../components/ActiveTargetIndicator';
import { useCareerTarget } from '../context/CareerTargetContext';
import { placementAPI, authAPI } from '../services/api';
import {
  ShieldCheck, CheckCircle2, AlertTriangle, AlertCircle, ArrowRight,
  TrendingUp, Sparkles, User, FileText, Building2, Layers,
  Zap, Target, Loader2, LogOut, RefreshCw, BarChart3
} from 'lucide-react';

export default function PlacementReadiness() {
  const navigate = useNavigate();
  const { activeTarget } = useCareerTarget();
  const [loading, setLoading] = useState(true);
  const [predicting, setPredicting] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  useEffect(() => {
    fetchLatestPrediction();
  }, []);

  const fetchLatestPrediction = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const data = await placementAPI.getMyPlacementReadiness();
      setPrediction(data);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to load placement prediction.');
    } finally {
      setLoading(false);
    }
  };

  const handleRunPrediction = async () => {
    setPredicting(true);
    setErrorMsg('');
    setSuccessMsg('');
    try {
      const res = await placementAPI.predictPlacement();
      setPrediction(res);
      setSuccessMsg('Placement readiness model re-evaluated with your latest profile attributes!');
    } catch (err) {
      setErrorMsg(err.message || 'Prediction failed.');
    } finally {
      setPredicting(false);
    }
  };

  const handleLogout = async () => {
    await authAPI.logout();
    navigate('/login');
  };

  const getScoreColor = (score) => {
    if (score >= 75) return { bg: '#dcfce7', text: '#15803d', bar: '#16a34a' };
    if (score >= 50) return { bg: '#fef3c7', text: '#b45309', bar: '#d97706' };
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
              Placement Readiness
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', margin: 0 }}>
              Placement probability evaluation based on academic standing, technical benchmarks, and project experience.
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

        {loading ? (
          <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
            <Loader2 size={32} className="animate-spin" style={{ color: 'var(--primary)', margin: '0 auto 1rem' }} />
            <p style={{ color: 'var(--text-muted)' }}>Running placement readiness inference...</p>
          </div>
        ) : prediction ? (
          <div>
            
            {/* Top Score Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6" style={{ marginBottom: '1.75rem' }}>
              
              {/* Placement Probability Card */}
              <div className="card" style={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                borderLeft: `5px solid ${getScoreColor(prediction.readiness_score).bar}`
              }}>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                    <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                      Placement Readiness Score
                    </span>
                    <span style={{
                      padding: '0.2rem 0.6rem',
                      borderRadius: '999px',
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      backgroundColor: getScoreColor(prediction.readiness_score).bg,
                      color: getScoreColor(prediction.readiness_score).text
                    }}>
                      {prediction.readiness_category}
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem', marginBottom: '0.75rem' }}>
                    <span style={{ fontSize: '2.75rem', fontWeight: 900, color: 'var(--text-main)', lineHeight: 1 }}>
                      {prediction.readiness_score}%
                    </span>
                    <span style={{ fontSize: '0.95rem', color: 'var(--text-muted)' }}>
                      ({Math.round(prediction.placement_probability * 100)}% Chance)
                    </span>
                  </div>

                  <div style={{ width: '100%', height: '8px', background: 'var(--border)', borderRadius: '999px', overflow: 'hidden' }}>
                    <div style={{
                      width: `${prediction.readiness_score}%`,
                      height: '100%',
                      background: getScoreColor(prediction.readiness_score).bar,
                      borderRadius: '999px',
                      transition: 'width 0.6s ease'
                    }} />
                  </div>
                </div>

                <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  <span>Status: <strong>{prediction.predicted_status}</strong></span>
                  <span>Model: <strong>{prediction.model_version}</strong></span>
                </div>
              </div>

              {/* Expected Salary Package */}
              <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#16a34a', marginBottom: '0.5rem' }}>
                    <TrendingUp size={18} />
                    <span style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase' }}>
                      Projected Compensation (CTC)
                    </span>
                  </div>

                  <div style={{ fontSize: '2.5rem', fontWeight: 900, color: 'var(--text-main)', lineHeight: 1.1, marginBottom: '0.4rem' }}>
                    {prediction.predicted_salary_min_lpa} - {prediction.predicted_salary_max_lpa} <span style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-muted)' }}>LPA</span>
                  </div>

                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>
                    Estimated baseline package for your competency tier based on market recruitment standards.
                  </p>
                </div>

                <div style={{ marginTop: '1rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Confidence index: <strong>{(prediction.confidence_score * 100).toFixed(0)}%</strong>
                </div>
              </div>

              {/* Action Re-Predict Card */}
              <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', background: 'var(--bg-subtle)' }}>
                <div>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 0.5rem 0' }}>
                    Live Model Evaluation
                  </h4>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: '1.5', margin: 0 }}>
                    Any updates to your CGPA, coding benchmarks, or internship records will instantly reflect here upon re-evaluation.
                  </p>
                </div>

                <button
                  onClick={handleRunPrediction}
                  disabled={predicting}
                  className="btn btn-primary"
                  style={{ width: '100%', padding: '0.65rem' }}
                >
                  {predicting ? (
                    <>
                      <Loader2 size={16} className="animate-spin" />
                      Evaluating Features...
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

            {/* Model Feature Breakdown */}
            {prediction.feature_breakdown && (
              <div className="card" style={{ marginBottom: '1.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                  <BarChart3 size={20} style={{ color: 'var(--primary)' }} />
                  <h3 style={{ fontSize: '1rem', fontWeight: 700, margin: 0, color: 'var(--text-main)' }}>
                    Live Candidate Features Evaluated by Random Forest Model
                  </h3>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4" style={{ textAlign: 'center', fontSize: '0.85rem' }}>
                  <div style={{ background: 'var(--bg-subtle)', padding: '0.75rem', borderRadius: '10px', border: '1px solid var(--border)' }}>
                    <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem' }}>CGPA</span>
                    <strong style={{ fontSize: '1.25rem', color: 'var(--text-main)' }}>{prediction.feature_breakdown.cgpa || '0.0'}</strong>
                  </div>

                  <div style={{ background: 'var(--bg-subtle)', padding: '0.75rem', borderRadius: '10px', border: '1px solid var(--border)' }}>
                    <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem' }}>Coding Benchmark</span>
                    <strong style={{ fontSize: '1.25rem', color: 'var(--primary)' }}>{prediction.feature_breakdown.coding_skill_score || '65'}/100</strong>
                  </div>

                  <div style={{ background: 'var(--bg-subtle)', padding: '0.75rem', borderRadius: '10px', border: '1px solid var(--border)' }}>
                    <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem' }}>Aptitude Score</span>
                    <strong style={{ fontSize: '1.25rem', color: '#818cf8' }}>{prediction.feature_breakdown.aptitude_score || '65'}/100</strong>
                  </div>

                  <div style={{ background: 'var(--bg-subtle)', padding: '0.75rem', borderRadius: '10px', border: '1px solid var(--border)' }}>
                    <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem' }}>Internships / Projects</span>
                    <strong style={{ fontSize: '1.25rem', color: '#10b981' }}>
                      {prediction.feature_breakdown.internships_count || 0} / {prediction.feature_breakdown.projects_count || 0}
                    </strong>
                  </div>
                </div>
              </div>
            )}

            {/* Strengths & Weak Areas */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6" style={{ marginBottom: '1.75rem' }}>
              
              {/* Positive Factors */}
              <div className="card">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                  <CheckCircle2 size={18} style={{ color: '#16a34a' }} />
                  <h3 style={{ fontSize: '0.95rem', fontWeight: 700, margin: 0, color: 'var(--text-main)' }}>
                    Top Positive Placement Factors
                  </h3>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {prediction.strengths.map((str, idx) => (
                    <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem', fontSize: '0.825rem', color: 'var(--text-main)' }}>
                      <span style={{ color: '#16a34a', fontWeight: 700 }}>✓</span>
                      <span>{str}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Risk Factors */}
              <div className="card">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                  <AlertTriangle size={18} style={{ color: '#dc2626' }} />
                  <h3 style={{ fontSize: '0.95rem', fontWeight: 700, margin: 0, color: 'var(--text-main)' }}>
                    Primary Risk Areas
                  </h3>
                </div>
                {prediction.weak_areas.length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {prediction.weak_areas.map((weak, idx) => (
                      <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem', fontSize: '0.825rem', color: 'var(--text-main)' }}>
                        <span style={{ color: '#dc2626', fontWeight: 700 }}>!</span>
                        <span>{weak}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p style={{ color: '#16a34a', fontSize: '0.85rem' }}>No critical risk factors detected!</p>
                )}
              </div>

            </div>

            {/* Improvement Suggestions */}
            {prediction.improvement_suggestions && prediction.improvement_suggestions.length > 0 && (
              <div className="card" style={{ marginBottom: '1.75rem', backgroundColor: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.3)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
                  <Zap size={18} style={{ color: '#f59e0b' }} />
                  <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#f59e0b', margin: 0 }}>
                    Actionable Improvement Directives
                  </h3>
                </div>
                <ul style={{ margin: 0, paddingLeft: '1.25rem', color: 'var(--text-main)', fontSize: '0.85rem', lineHeight: '1.7' }}>
                  {prediction.improvement_suggestions.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Next Step CTA */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
              <button
                onClick={() => navigate('/recommendations')}
                className="btn btn-primary"
                style={{ padding: '0.75rem 1.5rem', fontSize: '0.9rem' }}
              >
                Proceed to Personalized Recommendations
                <ArrowRight size={16} />
              </button>
            </div>

          </div>
        ) : null}

      </div>
    </div>
  );
}
