import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const dataPath = path.join(__dirname, 'store.json');

const seedData = {
  opportunities: [
    {
      id: 'opp_1',
      role: 'Senior Product Manager',
      company: 'Acme Health',
      source: 'Referral',
      stage: 'scouted',
      probability: 0.25,
      salary: 185000,
      equity: 20000,
      expectedValue: 51250,
      updatedAt: new Date().toISOString()
    }
  ],
  crm: {
    contacts: [
      {
        id: 'c_1',
        name: 'Maya Chen',
        company: 'Acme Health',
        title: 'VP Product',
        email: 'maya@example.com',
        linkedin: 'https://www.linkedin.com/in/example',
        notes: 'Warm intro via alumni network.'
      }
    ],
    interactions: [
      {
        id: 'i_1',
        contactId: 'c_1',
        channel: 'email',
        summary: 'Asked for referral process details.',
        createdAt: new Date().toISOString()
      }
    ],
    pipeline: [
      {
        opportunityId: 'opp_1',
        stage: 'scouted',
        owner: 'You',
        nextAction: 'Draft referral email'
      }
    ]
  },
  execution: {
    gmailDrafts: [],
    linkedInPrep: [],
    calendarEvents: []
  },
  metricsHistory: []
};

const ensureStore = () => {
  if (!fs.existsSync(dataPath)) {
    fs.writeFileSync(dataPath, JSON.stringify(seedData, null, 2), 'utf-8');
  }
};

export const readStore = () => {
  ensureStore();
  const raw = fs.readFileSync(dataPath, 'utf-8');
  return JSON.parse(raw);
};

export const writeStore = (data) => {
  fs.writeFileSync(dataPath, JSON.stringify(data, null, 2), 'utf-8');
};

export const withStore = (updater) => {
  const current = readStore();
  const updated = updater(current);
  writeStore(updated);
  return updated;
};
