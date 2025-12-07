import React, { useState, useEffect } from 'react';

// ===== AMAZING AGENT CARDS STYLES =====
const agentCardStyles = `
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

@keyframes shimmer {
  0% { background-position: -1000px 0; }
  100% { background-position: 1000px 0; }
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 20px rgba(102, 126, 234, 0.4); }
  50% { box-shadow: 0 0 40px rgba(102, 126, 234, 0.8), 0 0 60px rgba(102, 126, 234, 0.4); }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes progress-bar {
  0% { width: 0%; }
}

.agents-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 32px;
  padding: 20px 0;
  perspective: 1000px;
}

.agent-card {
  position: relative;
  padding: 32px;
  border-radius: 24px;
  cursor: pointer;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  transform-style: preserve-3d;
  overflow: hidden;
  min-height: 280px;
  display: flex;
  flex-direction: column;
  animation: slideInUp 0.6s ease forwards;
}

.agent-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 200%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.3),
    transparent
  );
  transition: left 0.5s;
}

.agent-card:hover::before {
  left: 100%;
}

.agent-card:hover {
  transform: translateY(-12px) scale(1.03);
}

.agent-card.active {
  grid-column: 1 / -1;
  min-height: 400px;
  transform: scale(1.02);
  animation: pulse-glow 2s infinite;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Email Agent - Green Gradient */
.agent-card.email {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
}

.agent-card.email:hover {
  box-shadow: 0 30px 80px rgba(102, 126, 234, 0.6);
}

/* Research Agent - Blue Gradient */
.agent-card.research {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  box-shadow: 0 20px 60px rgba(240, 147, 251, 0.4);
}

.agent-card.research:hover {
  box-shadow: 0 30px 80px rgba(240, 147, 251, 0.6);
}

/* Interview Agent - Orange Gradient */
.agent-card.interview {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  box-shadow: 0 20px 60px rgba(79, 172, 254, 0.4);
}

.agent-card.interview:hover {
  box-shadow: 0 30px 80px rgba(79, 172, 254, 0.6);
}

.agent-icon-large {
  font-size: 64px;
  margin-bottom: 16px;
  display: inline-block;
  animation: float 3s ease-in-out infinite;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.3));
}

.agent-card:hover .agent-icon-large {
  animation: float 1.5s ease-in-out infinite;
}

.agent-title {
  font-size: 28px;
  font-weight: 700;
  color: white;
  margin-bottom: 12px;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.agent-description {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 24px;
  line-height: 1.6;
}

.agent-features {
  list-style: none;
  padding: 0;
  margin: 0 0 24px 0;
}

.agent-feature {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  color: rgba(255, 255, 255, 0.95);
  font-size: 14px;
}

.agent-feature::before {
  content: '✓';
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  font-weight: bold;
}

.agent-action-btn {
  margin-top: auto;
  padding: 16px 24px;
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-radius: 12px;
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.agent-action-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.6);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
}

.agent-action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* Progress Section */
.progress-container {
  margin-top: 24px;
  padding: 24px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 16px;
  backdrop-filter: blur(10px);
}

.progress-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  color: white;
}

.progress-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.progress-title {
  font-size: 18px;
  font-weight: 600;
}

.progress-steps {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.progress-step {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: white;
  animation: slideInUp 0.4s ease forwards;
  opacity: 0;
}

.progress-step.active {
  background: rgba(255, 255, 255, 0.2);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.02); }
}

.progress-step.completed {
  opacity: 1;
}

.progress-step-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
  background: rgba(255, 255, 255, 0.3);
  flex-shrink: 0;
}

.progress-step.completed .progress-step-icon {
  background: #4ade80;
  animation: checkmark 0.5s ease;
}

@keyframes checkmark {
  0% { transform: scale(0); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

.progress-step-text {
  flex: 1;
  font-size: 14px;
  line-height: 1.4;
}

.progress-bar-container {
  margin-top: 20px;
  height: 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #4ade80, #22c55e);
  border-radius: 4px;
  transition: width 0.5s ease;
  animation: progress-bar 1s ease;
}

/* Close Button */
.close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.25);
  border: 2px solid rgba(255, 255, 255, 0.4);
  color: white;
  font-size: 20px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  z-index: 10;
  backdrop-filter: blur(10px);
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.4);
  transform: rotate(90deg) scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

/* Results Section */
.results-container {
  margin-top: 24px;
  padding: 24px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  color: #1a1a1a;
  max-height: 200px;
  overflow-y: auto;
}

.results-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #1a1a1a;
}

.results-content {
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
}

.action-buttons {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.btn-approve {
  flex: 1;
  padding: 14px 24px;
  background: linear-gradient(135deg, #4ade80, #22c55e);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-approve:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(74, 222, 128, 0.4);
}

.btn-cancel {
  flex: 1;
  padding: 14px 24px;
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-radius: 12px;
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

/* Animation delays for staggered appearance */
.agent-card:nth-child(1) { animation-delay: 0s; }
.agent-card:nth-child(2) { animation-delay: 0.1s; }
.agent-card:nth-child(3) { animation-delay: 0.2s; }
`;

const AgentPanel = ({ application }) => {
  const [activeAgent, setActiveAgent] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState([]);
  const [result, setResult] = useState(null);

  // Inject styles
  useEffect(() => {
    const styleId = 'agent-card-styles';
    if (!document.getElementById(styleId)) {
      const styleTag = document.createElement('style');
      styleTag.id = styleId;
      styleTag.textContent = agentCardStyles;
      document.head.appendChild(styleTag);
    }
    return () => {
      const existingStyle = document.getElementById(styleId);
      if (existingStyle) {
        existingStyle.remove();
      }
    };
  }, []);

  // Simulate progress updates
  useEffect(() => {
    if (loading && activeAgent) {
      const steps = getAgentSteps(activeAgent);
      let currentStep = 0;

      const interval = setInterval(() => {
        if (currentStep < steps.length) {
          setProgress(prev => [...prev, { ...steps[currentStep], completed: true }]);
          currentStep++;
        } else {
          clearInterval(interval);
        }
      }, 3000); // Update every 3 seconds

      return () => clearInterval(interval);
    }
  }, [loading, activeAgent]);

  const getAgentSteps = (agentType) => {
    const steps = {
      email: [
        { id: 1, text: 'Analyzing email tone and context...' },
        { id: 2, text: 'Selecting appropriate response template...' },
        { id: 3, text: 'Drafting professional response...' },
        { id: 4, text: 'Reviewing and formatting...' }
      ],
      research: [
        { id: 1, text: 'Searching company information...' },
        { id: 2, text: 'Analyzing recent news and updates...' },
        { id: 3, text: 'Gathering culture insights...' },
        { id: 4, text: 'Compiling comprehensive report...' }
      ],
      interview: [
        { id: 1, text: 'Analyzing job requirements...' },
        { id: 2, text: 'Generating practice questions...' },
        { id: 3, text: 'Creating study plan...' },
        { id: 4, text: 'Preparing interview guide...' }
      ]
    };
    return steps[agentType] || [];
  };

  const handleAgentClick = async (agentType) => {
    setActiveAgent(agentType);
    setLoading(true);
    setProgress([]);
    setResult(null);

    try {
      let endpoint = '';
      let payload = {};

      if (agentType === 'email') {
        endpoint = '/api/agents/email/draft';
        payload = {
          from: application.email_from,
          subject: application.email_subject,
          body: application.email_body || '',
          received_date: application.date_applied
        };
      } else if (agentType === 'research') {
        endpoint = '/api/agents/research';
        payload = {
          company: application.company,
          position: application.role,
          location: application.location || ''
        };
      } else if (agentType === 'interview') {
        endpoint = '/api/agents/interview-prep';
        payload = {
          company: application.company,
          position: application.role,
          interview_date: application.interview_date || new Date().toISOString(),
          available_hours: 20
        };
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (data.success) {
        setResult(data);
      } else {
        setResult({ error: 'Agent failed to complete task' });
      }
    } catch (error) {
      console.error('Agent error:', error);
      setResult({ error: error.message });
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setActiveAgent(null);
    setLoading(false);
    setProgress([]);
    setResult(null);
  };

  const handleApprove = async () => {
    if (!result) return;

    try {
      let endpoint = '';
      let payload = {};

      if (activeAgent === 'email') {
        endpoint = '/api/agents/email/send';
        payload = {
          approved: true,
          email_data: {
            from: application.email_from,
            subject: application.email_subject
          },
          draft: result.draft
        };
      } else if (activeAgent === 'research') {
        endpoint = '/api/agents/research/approve';
        payload = {
          approved: true,
          agent_state: result
        };
      } else if (activeAgent === 'interview') {
        endpoint = '/api/agents/interview-prep/approve';
        payload = {
          approved: true,
          agent_state: result
        };
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (data.success) {
        alert('✅ Action executed successfully!');
        handleClose();
      } else {
        alert('❌ Execution failed: ' + (data.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Approval error:', error);
      alert('❌ Error: ' + error.message);
    }
  };

  const agents = [
    {
      type: 'email',
      icon: '📧',
      title: 'Email Agent',
      description: 'Draft professional email responses with AI-powered tone matching and template selection.',
      features: ['Smart tone analysis', 'Template selection', 'Professional formatting']
    },
    {
      type: 'research',
      icon: '🔍',
      title: 'Research Agent',
      description: 'Deep dive into company information, news, culture, and insights to prepare you better.',
      features: ['Company analysis', 'Recent news', 'Culture insights']
    },
    {
      type: 'interview',
      icon: '📚',
      title: 'Interview Agent',
      description: 'Create personalized interview preparation plans with practice questions and study guides.',
      features: ['Practice questions', 'Study plans', 'Interview tips']
    }
  ];

  const progressPercentage = progress.length > 0
    ? (progress.length / getAgentSteps(activeAgent).length) * 100
    : 0;

  return (
    <div className="agents-container">
        {agents.map((agent) => (
          <div
            key={agent.type}
            className={`agent-card ${agent.type} ${activeAgent === agent.type ? 'active' : ''}`}
            onClick={(e) => {
              if (!activeAgent && !e.target.closest('.close-btn')) {
                handleAgentClick(agent.type);
              }
            }}
          >
            {activeAgent === agent.type && (
              <button className="close-btn" onClick={handleClose}>×</button>
            )}

            <div className="agent-icon-large">{agent.icon}</div>
            <h3 className="agent-title">{agent.title}</h3>
            <p className="agent-description">{agent.description}</p>

            <ul className="agent-features">
              {agent.features.map((feature, idx) => (
                <li key={idx} className="agent-feature">{feature}</li>
              ))}
            </ul>

            {activeAgent !== agent.type && (
              <button className="agent-action-btn">
                Launch Agent →
              </button>
            )}

            {activeAgent === agent.type && loading && (
              <div className="progress-container">
                <div className="progress-header">
                  <div className="progress-spinner"></div>
                  <span className="progress-title">Working...</span>
                </div>

                <div className="progress-steps">
                  {getAgentSteps(agent.type).map((step, idx) => (
                    <div
                      key={step.id}
                      className={`progress-step ${progress[idx]?.completed ? 'completed' : ''} ${idx === progress.length ? 'active' : ''}`}
                      style={{ animationDelay: `${idx * 0.1}s` }}
                    >
                      <div className="progress-step-icon">
                        {progress[idx]?.completed ? '✓' : idx + 1}
                      </div>
                      <div className="progress-step-text">{step.text}</div>
                    </div>
                  ))}
                </div>

                <div className="progress-bar-container">
                  <div
                    className="progress-bar-fill"
                    style={{ width: `${progressPercentage}%` }}
                  />
                </div>
              </div>
            )}

            {activeAgent === agent.type && !loading && result && (
              <div className="results-container">
                <h4 className="results-title">✨ Results Ready</h4>
                <div className="results-content">
                  {result.draft && `Draft: ${result.draft.substring(0, 200)}...`}
                  {result.status && `Status: ${result.status}`}
                  {result.error && `Error: ${result.error}`}
                </div>

                <div className="action-buttons">
                  <button className="btn-approve" onClick={handleApprove}>
                    ✓ Approve & Execute
                  </button>
                  <button className="btn-cancel" onClick={handleClose}>Close</button>
                </div>
              </div>
            )}
          </div>
        ))}
    </div>
  );
};

export default AgentPanel;
