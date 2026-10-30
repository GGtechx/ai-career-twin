import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';
import ResumeAnalysis from './pages/ResumeAnalysis';
import CompanyJobs from './pages/CompanyJobs';
import SkillGap from './pages/SkillGap';
import PlacementReadiness from './pages/PlacementReadiness';
import CareerRecommendations from './pages/CareerRecommendations';
import CareerRoadmap from './pages/CareerRoadmap';
import CareerAssistant from './pages/CareerAssistant';
import CareerTwin from './pages/CareerTwin';
import Dashboard from './pages/Dashboard';
import ProtectedRoute from './components/ProtectedRoute';
import { isAuthenticated } from './services/api';
import { CareerTargetProvider } from './context/CareerTargetContext';
import { ThemeProvider } from './context/ThemeContext';

export default function App() {
  return (
    <ThemeProvider>
      <CareerTargetProvider>
        <Router>
        <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          }
        />
        <Route
          path="/resume-analysis"
          element={
            <ProtectedRoute>
              <ResumeAnalysis />
            </ProtectedRoute>
          }
        />
        <Route path="/resume" element={<Navigate to="/resume-analysis" replace />} />
        <Route
          path="/companies-jobs"
          element={
            <ProtectedRoute>
              <CompanyJobs />
            </ProtectedRoute>
          }
        />
        <Route path="/companies-job" element={<Navigate to="/companies-jobs" replace />} />
        <Route path="/company-jobs" element={<Navigate to="/companies-jobs" replace />} />
        <Route path="/company-job" element={<Navigate to="/companies-jobs" replace />} />
        <Route path="/companies" element={<Navigate to="/companies-jobs" replace />} />
        <Route path="/company" element={<Navigate to="/companies-jobs" replace />} />
        <Route path="/jobs" element={<Navigate to="/companies-jobs" replace />} />
        <Route path="/job" element={<Navigate to="/companies-jobs" replace />} />
        <Route
          path="/skill-gap"
          element={
            <ProtectedRoute>
              <SkillGap />
            </ProtectedRoute>
          }
        />
        <Route
          path="/placement-readiness"
          element={
            <ProtectedRoute>
              <PlacementReadiness />
            </ProtectedRoute>
          }
        />
        <Route
          path="/placement"
          element={
            <ProtectedRoute>
              <PlacementReadiness />
            </ProtectedRoute>
          }
        />
        <Route
          path="/recommendations"
          element={
            <ProtectedRoute>
              <CareerRecommendations />
            </ProtectedRoute>
          }
        />
        <Route
          path="/roadmap"
          element={
            <ProtectedRoute>
              <CareerRoadmap />
            </ProtectedRoute>
          }
        />
        <Route
          path="/ai-assistant"
          element={
            <ProtectedRoute>
              <CareerAssistant />
            </ProtectedRoute>
          }
        />
        <Route
          path="/career-assistant"
          element={
            <ProtectedRoute>
              <CareerAssistant />
            </ProtectedRoute>
          }
        />
        <Route
          path="/career-twin"
          element={
            <ProtectedRoute>
              <CareerTwin />
            </ProtectedRoute>
          }
        />
        <Route
          path="/what-if"
          element={
            <ProtectedRoute>
              <CareerTwin />
            </ProtectedRoute>
          }
        />
        <Route
          path="/"
          element={
            isAuthenticated() ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
    </CareerTargetProvider>
    </ThemeProvider>
  );
}
