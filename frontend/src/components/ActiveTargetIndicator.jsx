import React from 'react';
import { Link } from 'react-router-dom';
import { useCareerTarget } from '../context/CareerTargetContext';
import { Target } from 'lucide-react';

export default function ActiveTargetIndicator({ compact = false, style = {} }) {
  const { activeTarget, loadingTarget } = useCareerTarget();

  const companyName = activeTarget?.company_name || activeTarget?.target_company_name;
  const jobTitle = activeTarget?.job_title || activeTarget?.title || activeTarget?.target_job_role;

  if (!companyName && !jobTitle) {
    return (
      <div
        className="active-target-badge"
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          padding: compact ? '4px 10px' : '6px 14px',
          background: 'var(--bg-subtle)',
          border: '1px dashed var(--border)',
          borderRadius: '8px',
          fontSize: compact ? '11px' : '12px',
          color: 'var(--text-muted)',
          ...style
        }}
      >
        <Target size={14} style={{ color: 'var(--text-dim)' }} />
        <span style={{ fontWeight: 600 }}>No Active Target</span>
        <Link
          to="/companies-jobs"
          style={{
            color: 'var(--primary)',
            textDecoration: 'none',
            fontWeight: 700,
            display: 'inline-flex',
            alignItems: 'center',
            gap: '3px'
          }}
        >
          Select Role →
        </Link>
      </div>
    );
  }

  return (
    <div
      className="active-target-badge"
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '8px',
        padding: compact ? '4px 10px' : '6px 14px',
        background: 'var(--primary-light)',
        border: '1px solid var(--border)',
        borderRadius: '8px',
        fontSize: compact ? '11px' : '12px',
        maxWidth: '100%',
        flexWrap: 'wrap',
        boxSizing: 'border-box',
        ...style
      }}
    >
      <Target size={14} style={{ color: 'var(--primary)' }} />
      <span
        style={{
          color: 'var(--primary)',
          fontWeight: 700,
          textTransform: 'uppercase',
          letterSpacing: '0.04em',
          fontSize: compact ? '10px' : '11px'
        }}
      >
        ACTIVE TARGET
      </span>
      <span style={{ color: 'var(--border)' }}>|</span>
      <span style={{ color: 'var(--text-main)', fontWeight: 700 }}>
        {companyName}
      </span>
      <span style={{ color: 'var(--text-dim)' }}>•</span>
      <span style={{ color: 'var(--text-muted)', fontWeight: 600 }}>
        {jobTitle}
      </span>
      {loadingTarget && (
        <span className="animate-spin" style={{ fontSize: '10px', color: 'var(--primary)' }}>
          ⟳
        </span>
      )}
    </div>
  );
}
