import express from 'express';
import cors from 'cors';
import { nanoid } from 'nanoid';
import { readStore, withStore } from './data/store.js';
import { computeExpectedValue, summarizeMetrics } from './services/revenueEngine.js';
import { startRuntimeLoop } from './runtime/loop.js';

const app = express();
app.use(cors());
app.use(express.json());

app.get('/health', (_req, res) => {
  res.json({ ok: true, service: 'CareerOS API' });
});

app.get('/api/state', (_req, res) => {
  const store = readStore();
  const metrics = summarizeMetrics(store.opportunities);
  res.json({ ...store, metrics });
});

app.post('/api/opportunities', (req, res) => {
  const payload = req.body;

  const created = {
    id: nanoid(10),
    role: payload.role,
    company: payload.company,
    source: payload.source || 'Manual',
    stage: 'scouted',
    probability: Number(payload.probability || 0.2),
    salary: Number(payload.salary || 0),
    equity: Number(payload.equity || 0),
    expectedValue: 0,
    updatedAt: new Date().toISOString()
  };

  created.expectedValue = computeExpectedValue(created);

  const updated = withStore((store) => ({
    ...store,
    opportunities: [created, ...store.opportunities],
    crm: {
      ...store.crm,
      pipeline: [
        {
          opportunityId: created.id,
          stage: created.stage,
          owner: 'You',
          nextAction: 'Research hiring manager'
        },
        ...store.crm.pipeline
      ]
    }
  }));

  res.status(201).json({ opportunity: created, count: updated.opportunities.length });
});

app.post('/api/crm/contacts', (req, res) => {
  const contact = { id: nanoid(10), ...req.body };
  const updated = withStore((store) => ({
    ...store,
    crm: {
      ...store.crm,
      contacts: [contact, ...store.crm.contacts]
    }
  }));
  res.status(201).json({ contact, count: updated.crm.contacts.length });
});

app.post('/api/execution/drafts', (req, res) => {
  const draft = {
    id: nanoid(10),
    type: req.body.type,
    subject: req.body.subject,
    body: req.body.body,
    relatedOpportunityId: req.body.relatedOpportunityId,
    status: 'pending_review',
    createdAt: new Date().toISOString()
  };

  withStore((store) => ({
    ...store,
    execution: {
      ...store.execution,
      gmailDrafts: [draft, ...store.execution.gmailDrafts]
    }
  }));

  res.status(201).json({ draft });
});

const port = process.env.PORT || 4000;
app.listen(port, () => {
  console.log(`CareerOS API listening on http://localhost:${port}`);
  startRuntimeLoop();
});
