const API_BASE = 'http://localhost:4000';

export const getState = async () => {
  const response = await fetch(`${API_BASE}/api/state`);
  if (!response.ok) throw new Error('Failed to load state');
  return response.json();
};

export const createOpportunity = async (payload) => {
  const response = await fetch(`${API_BASE}/api/opportunities`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!response.ok) throw new Error('Failed to create opportunity');
  return response.json();
};

export const createDraft = async (payload) => {
  const response = await fetch(`${API_BASE}/api/execution/drafts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!response.ok) throw new Error('Failed to create draft');
  return response.json();
};
