import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { careerTargetAPI, isAuthenticated } from '../services/api';

const CareerTargetContext = createContext(null);

export const ACTIVE_TARGET_KEY = 'career_twin_active_target';

export function CareerTargetProvider({ children }) {
  // 1. Initial State hydrated from localStorage for immediate, zero-flicker render
  const [activeTarget, setActiveTarget] = useState(() => {
    try {
      const stored = localStorage.getItem(ACTIVE_TARGET_KEY);
      return stored ? JSON.parse(stored) : null;
    } catch (e) {
      console.warn('Failed parsing active target from localStorage:', e);
      return null;
    }
  });

  const [loadingTarget, setLoadingTarget] = useState(false);
  const [targetVersion, setTargetVersion] = useState(0);

  // Helper to persist target to state and localStorage
  const updateTargetState = useCallback((target) => {
    setActiveTarget(target);
    setTargetVersion((v) => v + 1);
    if (target && (target.job_id || target.id)) {
      try {
        localStorage.setItem(ACTIVE_TARGET_KEY, JSON.stringify(target));
      } catch (e) {
        console.warn('Failed saving active target to localStorage:', e);
      }
    } else {
      localStorage.removeItem(ACTIVE_TARGET_KEY);
    }
  }, []);

  // 2. Fetch active target from single source of truth on backend
  const fetchActiveTarget = useCallback(async () => {
    if (!isAuthenticated()) return null;
    try {
      setLoadingTarget(true);
      const target = await careerTargetAPI.getCareerTarget();
      if (target && (target.job_id || target.id)) {
        updateTargetState(target);
        return target;
      }
    } catch (err) {
      console.warn('Could not fetch active career target from backend:', err);
    } finally {
      setLoadingTarget(false);
    }
    return null;
  }, [updateTargetState]);

  // 3. Centralized Target Selection Action
  const selectTargetJob = useCallback(async (jobId, companyId = null) => {
    if (!jobId) return;
    setLoadingTarget(true);
    try {
      const updated = await careerTargetAPI.setCareerTarget({
        job_id: jobId,
        company_id: companyId
      });
      if (updated && (updated.job_id || updated.id)) {
        updateTargetState(updated);
        return updated;
      }
    } catch (err) {
      console.error('Failed to set global active career target:', err);
      throw err;
    } finally {
      setLoadingTarget(false);
    }
  }, [updateTargetState]);

  // Sync with backend on initial load and authentication
  useEffect(() => {
    if (isAuthenticated()) {
      fetchActiveTarget();
    }
  }, [fetchActiveTarget]);

  return (
    <CareerTargetContext.Provider
      value={{
        activeTarget,
        setTargetJob: selectTargetJob,
        refreshTarget: fetchActiveTarget,
        loadingTarget,
        targetVersion
      }}
    >
      {children}
    </CareerTargetContext.Provider>
  );
}

export function useCareerTarget() {
  const context = useContext(CareerTargetContext);
  if (!context) {
    throw new Error('useCareerTarget must be used within a CareerTargetProvider');
  }
  return context;
}
