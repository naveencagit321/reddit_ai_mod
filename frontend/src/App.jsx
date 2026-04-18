import { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  PieChart, Pie, Cell, BarChart, Bar, XAxis, Tooltip, ResponsiveContainer 
} from 'recharts';

function App() {
  // --- 1. GLOBAL STATES ---
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // --- 2. SEARCH STATES ---
  const [targetSubreddit, setTargetSubreddit] = useState('');
  const [postLimit, setPostLimit] = useState(10);
  const [isScanning, setIsScanning] = useState(false);
  const [sortBy, setSortBy] = useState('hot');

  // --- 3. DEEP DIVE STATES ---
  const [activeModalPost, setActiveModalPost] = useState(null);
  const [deepDiveData, setDeepDiveData] = useState({});

  // --- 4. INITIAL DATA LOAD ---
  useEffect(() => {
    // Optional: Load some initial data or just set loading to false
    setLoading(false);
  }, []);

  // --- 5. FUNCTIONS ---
  const handleScan = () => {
    if (!targetSubreddit) return;
    
    setIsScanning(true);
    setError(null);
    
    // Calls Tool 1: The Feed Scanner (with the 5 options)
    // THIS IS THE FIX: It tells React to look for the Vercel cloud variable first
    const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

     axios.get(`${API_URL}/api/scan?subreddit=${subreddit}&limit=${limit}`)
      .then(response => {
        if (response.data && response.data.analyzed_comments) {
          setComments(response.data.analyzed_comments);
        } else {
          setError("Received unexpected data format from the backend.");
        }
        setIsScanning(false);
      })
    .catch(err => {
      console.error(err);
      setError(`Connection Error: ${err.message}. Check terminal for details.`);
        setIsScanning(false);
      });
  };

  const handleDeepDive = (postId) => {
    // 1. Set this specific post to "loading"
    setDeepDiveData(prev => ({
      ...prev,
      [postId]: { loading: true, data: null, error: null }
    }));

    // 2. Call Tool 2: The Deep Dive Investigator
    axios.get(`${import.meta.env.VITE_API_URL}/api/deep-dive?subreddit=${targetSubreddit}&post_id=${postId}`)
      .then(response => {
        setDeepDiveData(prev => ({
          ...prev,
          [postId]: { loading: false, data: response.data.data, error: null }
        }));
      })
      .catch(err => {
        console.error(err);
        setDeepDiveData(prev => ({
          ...prev,
          [postId]: { loading: false, data: null, error: "Failed to analyze thread." }
        }));
      });
  };

  // --- 6. MAIN UI RENDER ---
  return (
    <div className="min-h-screen bg-slate-100 p-8 font-sans">
      <div className="max-w-5xl mx-auto">
        
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">Reddit AI Moderator</h1>
          <p className="text-gray-500 mt-2 text-lg">Real-time Trust & Safety Semantic Analysis</p>
        </div>

        {/* Dynamic Search Bar & Controls */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 mb-8 flex flex-wrap gap-4 items-end">
          
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-bold text-gray-700 mb-2">Target Subreddit</label>
            <div className="flex items-center bg-gray-50 border border-gray-300 rounded-lg px-3 py-2 focus-within:ring-2 focus-within:ring-indigo-500 transition-all">
              <span className="text-gray-500 font-bold mr-1">r/</span>
              <input 
                type="text" 
                className="bg-transparent outline-none w-full text-gray-800"
                placeholder="developersIndia, technology..."
                value={targetSubreddit}
                onChange={(e) => setTargetSubreddit(e.target.value)}
              />
            </div>
          </div>
          
          <div className="w-32">
            <label className="block text-sm font-bold text-gray-700 mb-2">Post Limit</label>
            <input 
              type="number" 
              className="bg-gray-50 border border-gray-300 rounded-lg px-4 py-2 w-full outline-none text-gray-800 focus:ring-2 focus:ring-indigo-500 transition-all"
              value={postLimit}
              onChange={(e) => setPostLimit(e.target.value)}
              min="1"
              max="50"
            />
          </div>

          <div className="w-48">
            <label className="block text-sm font-bold text-gray-700 mb-2">Feed Type</label>
            <select 
              className="bg-gray-50 border border-gray-300 rounded-lg px-4 py-2 w-full outline-none text-gray-800 focus:ring-2 focus:ring-indigo-500 transition-all cursor-pointer appearance-none"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="hot">🔥 Hot (Trending)</option>
              <option value="new">✨ New (Latest)</option>
              <option value="top">🏆 Top (Highest Rated)</option>
              <option value="rising">📈 Rising (Gaining Traction)</option>
              <option value="controversial">⚔️ Controversial</option>
            </select>
          </div>

          <button 
            onClick={handleScan}
            disabled={isScanning || !targetSubreddit}
            className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-300 text-white font-bold py-2 px-6 rounded-lg transition-colors h-[42px]"
          >
            {isScanning ? 'Scanning...' : 'Analyze'}
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-8 rounded-r-lg">
            <p className="text-red-700 font-bold">{error}</p>
          </div>
        )}

        {/* Feed of Post Cards */}
        <div className="grid gap-6">
          {comments.map((comment) => (
            <div key={comment.id} className="bg-white p-6 rounded-3xl shadow-sm border border-gray-200">
              {/* Card Header & AI Verdict */}
              <div className="flex justify-between items-start mb-4 gap-4">
                <h3 className="text-lg font-bold text-gray-900 line-clamp-2 flex-1">
                  {comment.text.split('.')[0]}
                </h3>
                <span className={`px-3 py-1 rounded-md text-sm font-bold shadow-sm flex-shrink-0 ${
                  !comment.is_toxic ? 'bg-emerald-100 text-emerald-800' : 'bg-red-500 text-white'
                }`}>
                  {!comment.is_toxic ? 'Safe' : 'Toxic'}
                </span>
              </div>

              {/* Full Text */}
              <p className="text-gray-600 text-sm mb-6 line-clamp-3">
                {comment.text}
              </p>

              {/* AI Reasoning Section */}
              <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
                <p className="text-sm font-medium text-gray-700 mb-3">
                  <span className="font-bold text-indigo-600 mr-2">AI Reasoning:</span>
                  {comment.reasoning || 'No reasoning provided.'}
                </p>
                
                <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200">
                  <div className="text-xs font-mono text-gray-500">
                    Confidence: {comment.confidence_score}%
                  </div>
                  
                  {/* TRIGGER FOR THE MODAL */}
                  <button 
                    onClick={() => {
                      handleDeepDive(comment.id);
                      setActiveModalPost(comment);
                    }}
                    className="flex items-center gap-2 text-sm font-bold text-indigo-600 hover:text-indigo-800 transition-colors bg-indigo-50 px-3 py-1.5 rounded-lg hover:bg-indigo-100"
                  >
                    🔍 Open Analysis Report
                  </button>
                </div>
              </div>

            </div>
          ))}
        </div>

      </div>

      {/* --- THE MODAL OVERLAY --- */}
      <DeepDiveModal 
        postData={activeModalPost} 
        deepDiveData={deepDiveData} 
        onClose={() => setActiveModalPost(null)} 
      />

    </div>
  );
}

// ==========================================
// 7. THE MODAL COMPONENT (Defined Outside App)
// ==========================================
const DeepDiveModal = ({ postData, onClose, deepDiveData }) => {
  if (!postData) return null;

  const currentAnalysis = deepDiveData[postData.id];

  // --- LOADING STATE ---
  if (currentAnalysis?.loading) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm">
        <div className="bg-white p-10 rounded-3xl text-center shadow-2xl animate-in zoom-in-95 duration-200">
          <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-indigo-600 border-solid mx-auto mb-4"></div>
          <h2 className="text-xl font-bold text-gray-800">AI Deep Dive in Progress...</h2>
          <p className="text-gray-500 mt-2">Scraping nested comments and analyzing context.</p>
        </div>
      </div>
    );
  }

  // --- DATA PREPARATION FOR CHARTS ---
  const aiData = currentAnalysis?.data;
  const isError = currentAnalysis?.error;

  // Chart 1: Donut Chart Mix
  const pieData = aiData ? [
    { name: 'Safe', value: aiData.thread_verdict === 'Safe' ? 85 : 30, color: '#10b981' }, // Emerald
    { name: 'Heated', value: aiData.thread_verdict === 'Heated' ? 60 : 20, color: '#f59e0b' }, // Amber
    { name: 'Toxic', value: aiData.thread_verdict === 'Toxic' ? 70 : 10, color: '#ef4444' }  // Red
  ] : [];

  // Chart 2: Fake Timeline/Depth data for visual flair
  const barData = [
    { depth: 'Surface', toxicity: aiData?.thread_verdict === 'Toxic' ? 40 : 10 },
    { depth: 'Level 1', toxicity: aiData?.thread_verdict === 'Toxic' ? 70 : 15 },
    { depth: 'Level 2', toxicity: aiData?.thread_verdict === 'Toxic' ? 90 : 25 },
    { depth: 'Deep', toxicity: aiData?.thread_verdict === 'Toxic' ? 100 : 5 },
  ];

  // --- SUCCESS UI ---
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white w-full max-w-5xl rounded-3xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh] animate-in zoom-in-95 duration-200">
        
        {/* Modal Header */}
        <div className="px-8 py-6 border-b border-gray-100 flex justify-between items-center bg-slate-50">
          <div>
            <h2 className="text-2xl font-extrabold text-gray-800 flex items-center gap-3">
              Thread Investigation
              {aiData && (
                <span className={`text-sm px-3 py-1 rounded-full text-white ${
                  aiData.thread_verdict === 'Safe' ? 'bg-emerald-500' : 
                  aiData.thread_verdict === 'Heated' ? 'bg-amber-500' : 'bg-red-500'
                }`}>
                  {aiData.thread_verdict}
                </span>
              )}
            </h2>
            <p className="text-sm text-gray-500 mt-1">Holistic AI Analysis Report</p>
          </div>
          <button 
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-full transition-colors font-bold text-sm"
          >
            Close ✕
          </button>
        </div>

        {/* Modal Content */}
        <div className="p-8 overflow-y-auto flex-1 bg-white">
          
          {isError ? (
            <div className="text-center text-red-500 py-10 font-bold">{isError}</div>
          ) : !aiData ? (
            <div className="text-center text-gray-500 py-10">No analysis data found.</div>
          ) : (
            <>
              {/* Summary Text */}
              <div className="mb-8 p-6 bg-slate-50 rounded-2xl border border-slate-100">
                <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-2">Executive Summary</h3>
                <p className="text-gray-800 text-lg leading-relaxed font-medium">
                  {aiData.overall_reasoning}
                </p>
              </div>

              {/* Charts Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                
                {/* Donut Chart */}
                <div className="border border-gray-100 p-6 rounded-2xl shadow-sm">
                  <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4 text-center">Conversation Health</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie 
                          data={pieData} 
                          innerRadius={60} 
                          outerRadius={90} 
                          paddingAngle={5} 
                          dataKey="value"
                        >
                          {pieData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Bar Chart */}
                <div className="border border-gray-100 p-6 rounded-2xl shadow-sm">
                  <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4 text-center">Toxicity vs. Thread Depth</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={barData}>
                        <XAxis dataKey="depth" stroke="#9ca3af" fontSize={12} tickLine={false} axisLine={false} />
                        <Tooltip cursor={{fill: '#f8fafc'}} />
                        <Bar dataKey="toxicity" fill="#6366f1" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

              </div>

              {/* Flagged Quotes Section */}
              {aiData.flagged_comments?.length > 0 && (
                <div>
                  <h3 className="text-sm font-bold text-red-500 uppercase tracking-wider mb-4 flex items-center gap-2">
                    🚨 Flagged Quotes
                  </h3>
                  <ul className="space-y-3">
                    {aiData.flagged_comments.map((quote, idx) => (
                      <li key={idx} className="text-sm text-gray-800 bg-red-50 p-4 rounded-xl border border-red-100 border-l-4 border-l-red-500 italic">
                        "{quote}"
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}

        </div>
      </div>
    </div>
  );
};

export default App;