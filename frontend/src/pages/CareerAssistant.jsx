import React, { useState, useEffect, useRef } from 'react';
import Navbar from '../components/Navbar';
import ActiveTargetIndicator from '../components/ActiveTargetIndicator';
import { useCareerTarget } from '../context/CareerTargetContext';
import { aiAPI, profileAPI } from '../services/api';
import { MessageSquare, Send, Loader2, AlertCircle, BookOpen } from 'lucide-react';

export default function CareerAssistant() {
  const { activeTarget, targetVersion } = useCareerTarget();
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'assistant',
      text: "Hello! I am your Career Assistant. I have context of your profile, target job, skill gaps, and roadmap milestones. How can I guide your preparation today?",
      sources: [],
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [inputQuestion, setInputQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [studentContext, setStudentContext] = useState(null);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadInitialContext();
  }, [targetVersion, activeTarget?.id, activeTarget?.job_id]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const loadInitialContext = async () => {
    try {
      const prof = await profileAPI.getProfile();
      setStudentContext({
        student_name: prof.full_name || 'Student',
        target_role: activeTarget?.job_title || prof.target_job_role || 'Software Engineer',
        target_company: activeTarget?.company_name || prof.target_company || 'Target Company',
        cgpa: prof.cgpa || 7.5,
        coding_score: prof.coding_score || 65.0
      });
    } catch (err) {
      console.warn('Could not load preliminary profile context:', err);
    }
  };

  const handleSend = async (questionToSend) => {
    const q = (questionToSend || inputQuestion).trim();
    if (!q || loading) return;

    setError(null);
    const userMsgId = `u_${Date.now()}`;
    const userMessage = {
      id: userMsgId,
      sender: 'user',
      text: q,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMessage]);
    if (!questionToSend) setInputQuestion('');
    setLoading(true);

    try {
      const history = messages
        .filter((m) => m.id !== 'welcome')
        .map((m) => ({ role: m.sender, content: m.text }));

      const res = await aiAPI.askCareerAssistant(q, history);

      if (res.student_context) {
        setStudentContext(res.student_context);
      }

      const botMessage = {
        id: `a_${Date.now()}`,
        sender: 'assistant',
        text: res.answer,
        sources: res.retrieved_sources || [],
        followups: res.suggested_followups || [],
        is_fallback: res.is_fallback,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setError(err.message || 'Failed to get career guidance. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const quickPrompts = [
    "What skills should I prioritize learning for my target role?",
    "What project should I build to bridge my missing skills?",
    "How can I increase my placement readiness score?",
    "What interview topics should I prepare for this company?"
  ];

  return (
    <div className="min-h-screen" style={{ paddingBottom: '3rem' }}>
      <Navbar />
      <div className="container" style={{ marginTop: '1.5rem' }}>
        {/* Simple Page Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
          <div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)', margin: '0 0 0.25rem 0' }}>
              Career Assistant
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', margin: 0 }}>
              Ask questions about career guidance, interview preparation, and required competencies.
            </p>
          </div>
          <div>
            <ActiveTargetIndicator />
          </div>
        </div>

        {/* Main Grid: Sidebar + Chat Window */}
        <div
          className="ai-chat-grid"
          style={{
            display: 'grid',
            gridTemplateColumns: '280px minmax(0, 1fr)',
            gap: '1.5rem',
            alignItems: 'stretch'
          }}
        >
          {/* Left Context Panel */}
          <div
            className="card"
            style={{
              padding: '1.25rem',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between'
            }}
          >
            <div>
              <h3 style={{ margin: '0 0 1rem', fontSize: '0.875rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--text-main)' }}>
                Profile Overview
              </h3>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <div style={{ background: 'var(--bg-subtle)', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--border)' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Target Position</div>
                  <div style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '2px' }}>
                    {activeTarget?.job_title || studentContext?.target_role || 'Software Engineer'}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--primary)', fontWeight: 600 }}>
                    {activeTarget?.company_name || studentContext?.target_company || 'Target Company'}
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                  <div style={{ background: 'var(--bg-subtle)', padding: '10px', borderRadius: '8px', border: '1px solid var(--border)' }}>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Skill Match</div>
                    <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#16a34a', marginTop: '2px' }}>
                      {studentContext?.skill_match_percentage ?? 60.0}%
                    </div>
                  </div>
                  <div style={{ background: 'var(--bg-subtle)', padding: '10px', borderRadius: '8px', border: '1px solid var(--border)' }}>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Readiness</div>
                    <div style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--primary)', marginTop: '2px' }}>
                      {studentContext?.placement_readiness_score ?? 65.0}%
                    </div>
                  </div>
                </div>

                <div style={{ background: 'var(--bg-subtle)', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--border)' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Roadmap Stage</div>
                  <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#f59e0b', marginTop: '2px' }}>
                    {studentContext?.current_roadmap_stage || 'Skill Foundation'}
                  </div>
                </div>

                {studentContext?.top_missing_skills && studentContext.top_missing_skills.length > 0 && (
                  <div style={{ background: 'var(--bg-subtle)', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--border)' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600, marginBottom: '6px' }}>Identified Skill Gaps</div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                      {studentContext.top_missing_skills.map((s, idx) => (
                        <span key={idx} className="badge badge-danger" style={{ fontSize: '0.7rem' }}>
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div style={{ marginTop: '1.25rem', borderTop: '1px solid var(--border)', paddingTop: '12px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Responses are personalized based on your recorded profile metrics and selected target job.
              </div>
            </div>
          </div>

          {/* Right Chat Window */}
          <div
            className="card"
            style={{
              padding: 0,
              display: 'flex',
              flexDirection: 'column',
              height: '620px',
              overflow: 'hidden'
            }}
          >
            {/* Quick Prompts Bar */}
            <div
              style={{
                padding: '10px 14px',
                borderBottom: '1px solid var(--border)',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                flexWrap: 'wrap',
                background: 'var(--bg-subtle)'
              }}
            >
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, marginRight: '4px' }}>
                Suggestions:
              </span>
              {quickPrompts.map((p, i) => (
                <button
                  key={i}
                  onClick={() => handleSend(p)}
                  disabled={loading}
                  style={{
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border)',
                    color: 'var(--text-main)',
                    padding: '4px 10px',
                    borderRadius: '14px',
                    fontSize: '0.75rem',
                    cursor: 'pointer',
                    transition: 'all 0.15s'
                  }}
                  onMouseEnter={(e) => { e.target.style.background = 'var(--border)'; }}
                  onMouseLeave={(e) => { e.target.style.background = 'var(--bg-card)'; }}
                >
                  {p}
                </button>
              ))}
            </div>

            {/* Messages Container */}
            <div
              style={{
                flex: 1,
                padding: '1.25rem',
                overflowY: 'auto',
                display: 'flex',
                flexDirection: 'column',
                gap: '1rem',
                background: 'var(--bg-card)'
              }}
            >
              {messages.map((m) => (
                <div
                  key={m.id}
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: m.sender === 'user' ? 'flex-end' : 'flex-start',
                    width: '100%'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px', fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                    <span>{m.sender === 'user' ? 'You' : 'Assistant'}</span>
                    <span>•</span>
                    <span>{m.timestamp}</span>
                  </div>

                  <div
                    style={{
                      maxWidth: m.sender === 'user' ? '80%' : '88%',
                      padding: '12px 16px',
                      borderRadius: m.sender === 'user' ? '12px 12px 2px 12px' : '12px 12px 12px 2px',
                      background: m.sender === 'user' ? 'var(--primary)' : 'var(--bg-subtle)',
                      color: m.sender === 'user' ? '#ffffff' : 'var(--text-main)',
                      fontSize: '0.875rem',
                      lineHeight: '1.6',
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                      border: m.sender === 'user' ? 'none' : '1px solid var(--border)'
                    }}
                  >
                    {m.text}

                    {/* Retrieved Sources Accordion */}
                    {m.sources && m.sources.length > 0 && (
                      <div style={{ marginTop: '12px', paddingTop: '10px', borderTop: '1px solid var(--border)' }}>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700, marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <BookOpen size={13} /> Reference Sources ({m.sources.length}):
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                          {m.sources.map((s, idx) => (
                            <div key={idx} style={{ background: 'var(--bg-card)', padding: '6px 10px', borderRadius: '6px', border: '1px solid var(--border)', fontSize: '0.75rem' }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{s.title}</span>
                                <span style={{ fontSize: '0.7rem', color: 'var(--success)' }}>
                                  {(s.similarity_score * 100).toFixed(0)}% match
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Follow-up Prompts */}
                    {m.followups && m.followups.length > 0 && (
                      <div style={{ marginTop: '10px', display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                        {m.followups.map((f, i) => (
                          <button
                            key={i}
                            onClick={() => handleSend(f)}
                            style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', color: 'var(--text-main)', padding: '3px 8px', borderRadius: '10px', fontSize: '0.725rem', cursor: 'pointer' }}
                          >
                            {f}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {loading && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#2563eb', fontSize: '0.85rem', padding: '6px 0' }}>
                  <Loader2 size={16} className="animate-spin" />
                  <span>Preparing answer...</span>
                </div>
              )}

              {error && (
                <div className="alert alert-error" style={{ fontSize: '0.85rem' }}>
                  <AlertCircle size={16} />
                  <span>{error}</span>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input Box Footer */}
            <div style={{ padding: '12px 16px', borderTop: '1px solid var(--border)', background: 'var(--bg-subtle)' }}>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSend();
                }}
                style={{ display: 'flex', gap: '8px', alignItems: 'center' }}
              >
                <input
                  type="text"
                  value={inputQuestion}
                  onChange={(e) => setInputQuestion(e.target.value)}
                  placeholder="Ask about target skills, projects, placement readiness, or interview prep..."
                  disabled={loading}
                  className="form-input"
                  style={{ flex: 1, padding: '0.65rem 0.9rem' }}
                />
                <button
                  type="submit"
                  disabled={loading || !inputQuestion.trim()}
                  className="btn btn-primary"
                  style={{ padding: '0.65rem 1.25rem', flexShrink: 0 }}
                >
                  <Send size={15} />
                  <span>Send</span>
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @media (max-width: 900px) {
          .ai-chat-grid {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
}
