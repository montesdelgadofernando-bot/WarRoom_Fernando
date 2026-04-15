import { useEffect, useState } from 'react';
import { createDraft, createOpportunity, getState } from '../lib/api';

export const useCareerOS = () => {
  const [state, setState] = useState(null);
  const [loading, setLoading] = useState(true);

  const refresh = async () => {
    const data = await getState();
    setState(data);
  };

  useEffect(() => {
    refresh().finally(() => setLoading(false));
    const timer = setInterval(refresh, 5000);
    return () => clearInterval(timer);
  }, []);

  const addOpportunity = async (payload) => {
    await createOpportunity(payload);
    await refresh();
  };

  const addDraft = async (payload) => {
    await createDraft(payload);
    await refresh();
  };

  return { state, loading, addOpportunity, addDraft, refresh };
};
