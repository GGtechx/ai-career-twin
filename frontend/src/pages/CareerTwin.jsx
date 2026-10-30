import React, { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import Navbar from '../components/Navbar';
import ActiveTargetIndicator from '../components/ActiveTargetIndicator';
import { useCareerTarget } from '../context/CareerTargetContext';
import { twinAPI } from '../services/api';
import { RefreshCw, Play, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';

export default function CareerTwin() {
  const location = useLocation();
  const { activeTarget, targetVersion } = useCareerTarget();
  const isWhatIf = location.pathname.includes('/what-if');
  const whatIfRef = useRef(null);

  const [twin, setTwin] = useState(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState(null);

  // Simulation state
  const [simAddedSkills, setSimAddedSkills] = useState(['AWS', 'Docker']);
  const [customSkillInput, setCustomSkillInput] = useState('');
  const [simProjects, setSimProjects] = useState(1);
  const [simCodingDelta, setSimCodingDelta] = useState(10);
  const [simInternship, setSimInternship] = useState(0);
  const [simulating, setSimulating] = useState(false);
  const [simulationResult, setSimulationResult] = useState(null);

  useEffect(() => {
    loadTwinState();
  }, [targetVersion, activeTarget?.id, activeTarget?.job_id]);

  useEffect(() => {
    if (isWhatIf && whatIfRef.current) {
      whatIfRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [isWhatIf, loading]);

  const loadTwinState = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await twinAPI.getState();
      setTwin(data);
    } catch (err) {
      setError(err.message || 'Failed to load Career Twin state.');
    } finally {
      setLoading(false);
    }
  };

  const handleManualSync = async () => {
    setSyncing(true);
    try {
      const data = await twinAPI.sync('Manual User Dashboard Sync');
      setTwin(data);
    } catch (err) {
      setError(err.message || 'Sync failed.');
    } finally {
      setSyncing(false);
    }
  };

  const handleRunSimulation = async () => {
    setSimulating(true);
    try {
      const payload = {
        added_skills: simAddedSkills,
        added_projects_count: simProjects,
        coding_score_delta: simCodingDelta,
        aptitude_score_delta: 5.0,
        added_internships_count: simInternship
      };
      const res = await twinAPI.simulate(payload);
      setSimulationResult(res);
    } catch (err) {
      setError(err.message || 'Simulation execution failed.');
    } finally {
      setSimulating(false);
    }
  };

  const handleAddSkillTag = () => {
    const val = customSkillInput.trim();
    if (val && !simAddedSkills.includes(val)) {
      setSimAddedSkills([...simAddedSkills, val]);
      setCustomSkillInput('');
    }
  };

  const handleRemoveSkillTag = (skillToRemove) => {
    setSimAddedSkills(simAddedSkills.filter((s) => s !== skillToRemove));
  };

  if (loading) {
    return (
      <div className="min-h-screen">
        <Navbar />
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 'calc(100vh - 64px)' }}>
          <div style={{ textAlign: 'center' }}>
            <Loader2 size={32} className="animate-spin" style={{ color: 'var(--primary)', margin: '0 auto 16px' }} />
            <p style={{ color: 'var(--text-muted)', fontSize: '15px' }}>Loading Career Twin model...</p>
          </div>
        </div>
      </div>
    );
  }

  const radar = twin?.radar_breakdown || {
    Coding: 65,
    Aptitude: 65,
    Projects: 60,
    Communication: 65,
    Logical: 65,
    Leadership: 60
  };

  return (
    <div className="min-h-screen" style={{ paddingBottom: '3rem' }}>
      <Navbar />
      <div className="container" style={{ marginTop: '1.5rem' }}>
        {/* Simple Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h1 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)' }}>
                Career Twin
              </h1>
              <span className="badge badge-blue">
                v{twin?.twin_version || 1}
              </span>
            </div>
            <p style={{ margin: '4px 0 0', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
              Dynamic model of student competencies, career metrics, and scenario simulations.
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
            <ActiveTargetIndicator />
            <button
              onClick={handleManualSync}
              disabled={syncing}
              className="btn btn-secondary"
              style={{ fontSize: '0.85rem' }}
            >
              <RefreshCw size={14} className={syncing ? 'animate-spin' : ''} />
              <span>{syncing ? 'Syncing...' : 'Sync Twin'}</span>
            </button>
          </div>
        </div>

        {error && (
          <div className="alert alert-error" style={{ marginBottom: '1.25rem' }}>
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        {/* 3 Metric Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
          {/* Overall Twin Score */}
          <div className="card">
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>Overall Twin Score</div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px', marginTop: '6px' }}>
              <span style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--text-main)' }}>
                {twin?.overall_twin_score || 64.0}
              </span>
              <span style={{ fontSize: '0.875rem', color: 'var(--text-dim)' }}>/ 100</span>
            </div>
            <div style={{ marginTop: '10px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span className="badge badge-green">
                Top {(100 - (twin?.benchmark_percentile || 50)).toFixed(0)}% of Cohort
              </span>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>({twin?.benchmark_percentile}th percentile)</span>
            </div>
          </div>

          {/* Target Alignment */}
          <div className="card">
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>Target Alignment</div>
            <div style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '4px' }}>
              {activeTarget?.job_title || twin?.target_role || 'Software Engineer'}
            </div>
            <div style={{ fontSize: '0.85rem', color: 'var(--primary)', fontWeight: 600 }}>
              {activeTarget?.company_name || twin?.target_company || 'Target Enterprise'}
            </div>
            <div style={{ display: 'flex', gap: '16px', marginTop: '10px' }}>
              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Skill Match</div>
                <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#16a34a' }}>{twin?.skill_match_percentage}%</div>
              </div>
              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Roadmap Stage</div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#f59e0b', marginTop: '2px' }}>{twin?.current_roadmap_stage}</div>
              </div>
            </div>
          </div>

          {/* Placement Projection */}
          <div className="card">
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>Placement Projection</div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px', marginTop: '6px' }}>
              <span style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--text-main)' }}>
                {twin?.projected_placement_chance}%
              </span>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>chance</span>
            </div>
            <div style={{ marginTop: '10px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Est. Package: <strong style={{ color: 'var(--text-main)' }}>{twin?.projected_salary_lpa} LPA</strong>
            </div>
          </div>
        </div>

        {/* Grid: Competency Vector + Simulation */}
        <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '1.5rem', alignItems: 'start' }}>
          {/* Competency Bars */}
          <div className="card">
            <h3 style={{ margin: '0 0 1rem', fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-main)' }}>
              Competency Breakdown
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {Object.entries(radar).map(([dim, score]) => (
                <div key={dim}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '3px' }}>
                    <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{dim}</span>
                    <span style={{ fontWeight: 700, color: score >= 75 ? '#16a34a' : score >= 60 ? '#d97706' : '#dc2626' }}>
                      {score}/100
                    </span>
                  </div>
                  <div style={{ height: '7px', background: 'var(--border)', borderRadius: '4px', overflow: 'hidden' }}>
                    <div
                      style={{
                        height: '100%',
                        width: `${Math.min(100, Math.max(0, score))}%`,
                        background: score >= 75 ? '#16a34a' : score >= 60 ? '#d97706' : '#dc2626',
                        borderRadius: '4px',
                        transition: 'width 0.5s ease-out'
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>

            {/* Timeline */}
            <div style={{ marginTop: '1.5rem', borderTop: '1px solid var(--border)', paddingTop: '1rem' }}>
              <h4 style={{ margin: '0 0 10px', fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                Recent Milestone Updates
              </h4>
              {twin?.timeline && twin.timeline.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {twin.timeline.map((item, idx) => (
                    <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '0.8rem' }}>
                      <CheckCircle2 size={14} style={{ color: '#16a34a', flexShrink: 0, marginTop: '2px' }} />
                      <div style={{ flex: 1 }}>
                        <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>{item.title}</div>
                        <div style={{ color: 'var(--text-muted)', fontSize: '0.725rem' }}>
                          {item.category} • {item.date}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p style={{ color: '#64748b', fontSize: '0.8rem', margin: 0 }}>No updates logged yet.</p>
              )}
            </div>
          </div>

          {/* Simulation Box */}
          <div ref={whatIfRef} className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem', flexWrap: 'wrap', gap: '8px' }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)' }}>
                  What-If Career Simulation
                </h3>
                <p style={{ margin: '3px 0 0', color: 'var(--text-muted)', fontSize: '0.825rem' }}>
                  Test hypothetical skill additions, projects, and benchmark increases to predict placement impact.
                </p>
              </div>
              <span className="badge badge-purple">
                Sandbox Mode
              </span>
            </div>

            {/* Simulation Controls */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', background: 'var(--bg-subtle)', padding: '1rem', borderRadius: '10px', border: '1px solid var(--border)', marginBottom: '1.25rem' }}>
              {/* Added Skills Tag Manager */}
              <div>
                <label className="form-label" style={{ fontSize: '0.8rem' }}>
                  Simulate Adding Skills:
                </label>
                <div style={{ display: 'flex', gap: '6px', marginBottom: '6px' }}>
                  <input
                    type="text"
                    value={customSkillInput}
                    onChange={(e) => setCustomSkillInput(e.target.value)}
                    onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleAddSkillTag(); } }}
                    placeholder="e.g. AWS, Docker"
                    className="form-input"
                    style={{ fontSize: '0.8rem', padding: '0.4rem 0.6rem' }}
                  />
                  <button
                    type="button"
                    onClick={handleAddSkillTag}
                    className="btn btn-secondary"
                    style={{ fontSize: '0.75rem', padding: '0.4rem 0.8rem' }}
                  >
                    Add
                  </button>
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                  {simAddedSkills.map((s) => (
                    <span key={s} className="tag-removable" style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem' }}>
                      {s}
                      <button onClick={() => handleRemoveSkillTag(s)}>×</button>
                    </span>
                  ))}
                </div>
              </div>

              {/* Slider: Coding Score Boost */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--text-main)', fontWeight: 600, marginBottom: '6px' }}>
                  <span>Coding Score Boost:</span>
                  <span style={{ color: 'var(--primary)', fontWeight: 700 }}>+{simCodingDelta} pts</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="30"
                  step="5"
                  value={simCodingDelta}
                  onChange={(e) => setSimCodingDelta(Number(e.target.value))}
                  style={{ width: '100%', cursor: 'pointer', accentColor: 'var(--primary)' }}
                />
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-dim)' }}>
                  <span>+0</span>
                  <span>+15</span>
                  <span>+30</span>
                </div>
              </div>

              {/* Projects & Internships */}
              <div style={{ display: 'flex', gap: '8px' }}>
                <div style={{ flex: 1 }}>
                  <label className="form-label" style={{ fontSize: '0.8rem' }}>
                    Add Projects:
                  </label>
                  <select
                    value={simProjects}
                    onChange={(e) => setSimProjects(Number(e.target.value))}
                    className="form-select"
                    style={{ fontSize: '0.8rem', padding: '0.4rem 0.6rem' }}
                  >
                    <option value={0}>0 projects</option>
                    <option value={1}>+1 Project</option>
                    <option value={2}>+2 Projects</option>
                  </select>
                </div>

                <div style={{ flex: 1 }}>
                  <label className="form-label" style={{ fontSize: '0.8rem' }}>
                    Add Internship:
                  </label>
                  <select
                    value={simInternship}
                    onChange={(e) => setSimInternship(Number(e.target.value))}
                    className="form-select"
                    style={{ fontSize: '0.8rem', padding: '0.4rem 0.6rem' }}
                  >
                    <option value={0}>0 internships</option>
                    <option value={1}>+1 Internship</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Run Button */}
            <div style={{ marginBottom: '1.25rem' }}>
              <button
                onClick={handleRunSimulation}
                disabled={simulating}
                className="btn btn-primary"
                style={{ padding: '0.65rem 1.25rem', fontSize: '0.875rem' }}
              >
                {simulating ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    <span>Calculating Simulation...</span>
                  </>
                ) : (
                  <>
                    <Play size={15} />
                    <span>Run Simulation</span>
                  </>
                )}
              </button>
            </div>

            {/* Simulation Output */}
            {simulationResult && (
              <div style={{ background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.25)', borderRadius: '10px', padding: '1.25rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#10b981', textTransform: 'uppercase' }}>
                    Simulation Projection
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    {new Date(simulationResult.simulated_at).toLocaleTimeString()}
                  </div>
                </div>

                <div style={{ fontSize: '0.875rem', color: 'var(--text-main)', lineHeight: '1.5', marginBottom: '1rem' }}>
                  {simulationResult.analysis_summary}
                </div>

                {/* Comparison Metric Cards */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '8px', marginBottom: '1rem' }}>
                  <div style={{ background: 'var(--bg-card)', padding: '10px', borderRadius: '8px', border: '1px solid var(--border)' }}>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Skill Match</div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#16a34a', marginTop: '2px' }}>
                      {simulationResult.simulated.skill_match_percentage}%
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#15803d', fontWeight: 600 }}>
                      +{simulationResult.deltas.match_percentage_delta}% gain
                    </div>
                  </div>

                  <div style={{ background: 'var(--bg-card)', padding: '10px', borderRadius: '8px', border: '1px solid var(--border)' }}>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Readiness</div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--primary)', marginTop: '2px' }}>
                      {simulationResult.simulated.placement_readiness_score}%
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--primary)', fontWeight: 600 }}>
                      +{simulationResult.deltas.placement_readiness_delta}% gain
                    </div>
                  </div>

                  <div style={{ background: 'var(--bg-card)', padding: '10px', borderRadius: '8px', border: '1px solid var(--border)' }}>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Placement Chance</div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#818cf8', marginTop: '2px' }}>
                      {simulationResult.simulated.projected_placement_chance}%
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#818cf8', fontWeight: 600 }}>
                      +{simulationResult.deltas.placement_chance_delta}%
                    </div>
                  </div>

                  <div style={{ background: 'var(--bg-card)', padding: '10px', borderRadius: '8px', border: '1px solid var(--border)' }}>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Est. Salary</div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f59e0b', marginTop: '2px' }}>
                      {simulationResult.simulated.projected_salary_lpa} LPA
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#f59e0b', fontWeight: 600 }}>
                      +{simulationResult.deltas.salary_delta_lpa} LPA lift
                    </div>
                  </div>
                </div>

                {simulationResult.resolved_skills && simulationResult.resolved_skills.length > 0 && (
                  <div>
                    <span style={{ fontSize: '0.75rem', color: '#10b981', fontWeight: 700 }}>
                      Gaps Resolved:
                    </span>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '4px' }}>
                      {simulationResult.resolved_skills.map((s, i) => (
                        <span key={i} className="badge badge-green" style={{ fontSize: '0.725rem' }}>
                          ✓ {s}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      <style>{`
        @media (max-width: 900px) {
          .container > div:last-child {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
}
