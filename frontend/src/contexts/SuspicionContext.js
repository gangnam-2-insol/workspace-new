import React, { createContext, useContext, useState } from 'react';

const SuspicionContext = createContext();

export const useSuspicion = () => {
  const context = useContext(SuspicionContext);
  if (!context) {
    throw new Error('useSuspicion must be used within a SuspicionProvider');
  }
  return context;
};

export const SuspicionProvider = ({ children }) => {
  const [suspicionData, setSuspicionData] = useState({});
  const [loadingSuspicion, setLoadingSuspicion] = useState({});

  const updateSuspicionData = (applicantId, data) => {
    setSuspicionData(prev => ({
      ...prev,
      [applicantId]: data
    }));
  };

  const setLoadingState = (applicantId, isLoading) => {
    setLoadingSuspicion(prev => ({
      ...prev,
      [applicantId]: isLoading
    }));
  };

  const getSuspicionData = (applicantId) => {
    return suspicionData[applicantId] || null;
  };

  const getLoadingState = (applicantId) => {
    return loadingSuspicion[applicantId] || false;
  };

  const value = {
    suspicionData,
    loadingSuspicion,
    updateSuspicionData,
    setLoadingState,
    getSuspicionData,
    getLoadingState
  };

  return (
    <SuspicionContext.Provider value={value}>
      {children}
    </SuspicionContext.Provider>
  );
};