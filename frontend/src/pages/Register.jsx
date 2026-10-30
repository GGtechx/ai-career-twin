import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authAPI } from '../services/api';
import { useTheme } from '../context/ThemeContext';
import { Mail, Lock, User, GraduationCap, Building2, ArrowRight, AlertCircle, Loader2, Sun, Moon } from 'lucide-react';

export default function Register() {
  const navigate = useNavigate();
  const { theme, toggleTheme, isDark } = useTheme();
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
    college_name: '',
    degree: 'B.Tech',
    branch: 'CSE'
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }

    setLoading(true);

    try {
      await authAPI.register(formData);
      navigate('/profile');
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ position: 'relative', padding: '2rem 1.5rem' }}>
      {/* Top Right Theme Toggle */}
      <button
        onClick={toggleTheme}
        type="button"
        style={{
          position: 'absolute',
          top: '20px',
          right: '20px',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          background: 'var(--bg-card)',
          border: '1px solid var(--border)',
          color: 'var(--text-main)',
          padding: '6px 14px',
          borderRadius: '8px',
          fontSize: '12px',
          fontWeight: 600,
          cursor: 'pointer'
        }}
      >
        {isDark ? <Sun size={14} style={{ color: '#fbbf24' }} /> : <Moon size={14} style={{ color: '#2563eb' }} />}
        <span>{isDark ? 'Light Mode' : 'Dark Mode'}</span>
      </button>

      <div className="card" style={{ width: '100%', maxWidth: '500px', padding: '2rem' }}>
        
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <div style={{ width: '44px', height: '44px', borderRadius: '10px', background: '#2563eb', color: '#fff', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: '18px', fontWeight: 800, marginBottom: '0.75rem' }}>
            CT
          </div>
          <h1 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.25rem' }}>
            Create Student Account
          </h1>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Set up your student profile and career targets
          </p>
        </div>

        {error && (
          <div className="alert alert-error">
            <AlertCircle size={18} style={{ flexShrink: 0 }} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="full_name">Full Name</label>
            <div style={{ position: 'relative' }}>
              <input
                id="full_name"
                name="full_name"
                type="text"
                required
                placeholder="e.g. John Doe"
                className="form-input"
                style={{ paddingLeft: '2.5rem' }}
                value={formData.full_name}
                onChange={handleChange}
              />
              <User size={16} style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }} />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="email">College / Personal Email</label>
            <div style={{ position: 'relative' }}>
              <input
                id="email"
                name="email"
                type="email"
                required
                placeholder="student@university.edu"
                className="form-input"
                style={{ paddingLeft: '2.5rem' }}
                value={formData.email}
                onChange={handleChange}
              />
              <Mail size={16} style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }} />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="password">Password (min 6 characters)</label>
            <div style={{ position: 'relative' }}>
              <input
                id="password"
                name="password"
                type="password"
                required
                placeholder="••••••••"
                className="form-input"
                style={{ paddingLeft: '2.5rem' }}
                value={formData.password}
                onChange={handleChange}
              />
              <Lock size={16} style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }} />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="form-group">
              <label className="form-label" htmlFor="degree">Degree</label>
              <select
                id="degree"
                name="degree"
                className="form-select"
                value={formData.degree}
                onChange={handleChange}
              >
                <option value="B.Tech">B.Tech / B.E.</option>
                <option value="M.Tech">M.Tech / M.E.</option>
                <option value="BCA">BCA</option>
                <option value="MCA">MCA</option>
                <option value="B.Sc CS">B.Sc Computer Science</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="branch">Branch / Department</label>
              <select
                id="branch"
                name="branch"
                className="form-select"
                value={formData.branch}
                onChange={handleChange}
              >
                <option value="CSE">Computer Science (CSE)</option>
                <option value="IT">Information Tech (IT)</option>
                <option value="AI_DS">AI & Data Science</option>
                <option value="ECE">Electronics & Comm (ECE)</option>
                <option value="EEE">Electrical & Electronics (EEE)</option>
                <option value="Mechanical">Mechanical Engineering</option>
                <option value="Civil">Civil Engineering</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="college_name">College / University Name</label>
            <div style={{ position: 'relative' }}>
              <input
                id="college_name"
                name="college_name"
                type="text"
                placeholder="e.g. Apex Institute of Technology"
                className="form-input"
                style={{ paddingLeft: '2.5rem' }}
                value={formData.college_name}
                onChange={handleChange}
              />
              <Building2 size={16} style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }} />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '0.75rem', padding: '0.75rem' }}
          >
            {loading ? (
              <>
                <Loader2 size={18} className="animate-spin" />
                Registering Account...
              </>
            ) : (
              <>
                Complete Registration
                <ArrowRight size={16} />
              </>
            )}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '1.75rem', fontSize: '0.875rem', color: '#64748b' }}>
          Already have an account?{' '}
          <Link to="/login" style={{ color: '#2563eb', fontWeight: 600, textDecoration: 'none' }}>
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
}
