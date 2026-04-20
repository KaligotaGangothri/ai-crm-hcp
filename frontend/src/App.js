import React, { useState } from "react";
import axios from "axios";
import {
  TextField,
  Button,
  Card,
  Typography,
  MenuItem,
  Radio,
  RadioGroup,
  FormControlLabel,
  InputAdornment,
  Box,
  Divider
} from "@mui/material";

// Icons
import SearchIcon from "@mui/icons-material/Search";
import AddIcon from "@mui/icons-material/Add";
import CalendarTodayIcon from "@mui/icons-material/CalendarToday";
import AccessTimeIcon from "@mui/icons-material/AccessTime";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";

const API = "http://127.0.0.1:8000";

function App() {
  const [form, setForm] = useState({
    doctor_name: "",
    interaction_type: "Meeting",
    date: "DD-MM-YYYY",
    time: "__:__",
    attendees: "",
    topics: "",
    sentiment: "neutral",
    outcomes: "",
    followups: "",
  });

  const [chat, setChat] = useState("");
  
  // State to hold the chat history bubbles
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      type: "info",
      text: "Log interaction details here (e.g., \"Met Dr. Smith, on 20-04-2026 at 11:11, Rahul and Akshay, discussed Product X efficacy, positive sentiment, shared brochure\") or ask for help."
    }
  ]);

  const aiFollowups = [
    "+ Schedule follow-up meeting in 2 weeks",
    "+ Send OncoBoost Phase III PDF",
    "+ Add Dr. Sharma to advisory board invite list",
  ];

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleChat = async () => {
    if (!chat.trim()) return;

    const userMessage = chat;
    setChat(""); // Clear input box immediately

    // Add User's message bubble to the UI
    setMessages((prev) => [
      ...prev,
      { role: "user", text: userMessage }
    ]);

    try {
      const response = await axios.post(`${API}/ai-chat`, { message: userMessage });
      
      // 1. Safely extract the payload (handles if backend nests it inside 'data' or 'output')
      const aiData = response.data.data || response.data.output || response.data;
      
      // 2. Look for the doctor's name to confirm it's an extraction event
      const extractedDoctorName = aiData.doctor_name || aiData.hcp_name;

      if (extractedDoctorName) {
        
        // --- CLEANUP LOGIC FOR INTERACTION TYPE ---
        let rawType = aiData.interaction_type || "Meeting";
        let cleanType = rawType.charAt(0).toUpperCase() + rawType.slice(1).toLowerCase();
        
        // Ensure it exactly matches the Material UI Dropdown options
        if (!["Meeting", "Call", "Email"].includes(cleanType)) {
            cleanType = "Meeting";
        }
        // ------------------------------------------

        // 3. EXPLICITLY map the backend keys to your frontend form state
        setForm((prevForm) => ({
          ...prevForm,
          doctor_name: extractedDoctorName,
          interaction_type: cleanType, // Use the cleaned variable here!
          date: aiData.date || prevForm.date,
          time: aiData.time || prevForm.time,
          attendees: aiData.attendees || aiData.representatives_present || prevForm.attendees,
          topics: aiData.topics || aiData.topics_discussed || prevForm.topics,
          sentiment: aiData.sentiment ? aiData.sentiment.toLowerCase() : "neutral"
        }));
        
        // Add AI Success bubble to the UI
        setMessages((prev) => [
          ...prev,
          { 
            role: "assistant", 
            type: "success", 
            text: "✅ Interaction logged successfully! The details have been automatically populated." 
          }
        ]);
      } else {
        // Handle general chat response (could be text or a tool object)
        setMessages((prev) => [
          ...prev,
          { 
            role: "assistant", 
            type: "chat", 
            text: response.data.output || response.data 
          }
        ]);
      }
    } catch (error) {
      console.error("Failed to log interaction", error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", type: "error", text: "❌ Error connecting to AI backend. Check terminal for crashes." }
      ]);
    }
  };

  return (
    <div style={{ display: "flex", height: "100vh", background: "#f8f9fa", fontFamily: "Inter, sans-serif" }}>
      
      {/* LEFT PANEL: STRUCTURED FORM */}
      <div style={{ flex: 7, padding: "24px 32px", overflowY: "auto" }}>
        <Typography variant="h5" style={{ fontWeight: 600, color: "#1a1a1a", marginBottom: 20 }}>
          Log HCP Interaction
        </Typography>

        <Card style={{ padding: 32, borderRadius: 8, boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }} elevation={0}>
          <SectionHeader title="Interaction Details" />

          {/* HCP & TYPE ROW */}
          <Box sx={{ display: "flex", justifyContent: "space-between", marginBottom: 2.5 }}>
            <Box sx={{ width: "48%" }}>
              <InputLabel>HCP Name</InputLabel>
              <TextField fullWidth size="small" placeholder="Search or select HCP..." name="doctor_name" value={form.doctor_name} onChange={handleChange} />
            </Box>
            <Box sx={{ width: "48%" }}>
              <InputLabel>Interaction Type</InputLabel>
              <TextField fullWidth size="small" select name="interaction_type" value={form.interaction_type} onChange={handleChange}>
                <MenuItem value="Meeting">Meeting</MenuItem>
                <MenuItem value="Call">Call</MenuItem>
                <MenuItem value="Email">Email</MenuItem>
              </TextField>
            </Box>
          </Box>

          {/* DATE & TIME ROW */}
          <Box sx={{ display: "flex", justifyContent: "space-between", marginBottom: 2.5 }}>
            <Box sx={{ width: "48%" }}>
              <InputLabel>Date</InputLabel>
              <TextField fullWidth size="small" name="date" value={form.date} onChange={handleChange} InputProps={{ startAdornment: <InputAdornment position="start"><CalendarTodayIcon fontSize="small" /></InputAdornment> }} />
            </Box>
            <Box sx={{ width: "48%" }}>
              <InputLabel>Time</InputLabel>
              <TextField fullWidth size="small" name="time" value={form.time} onChange={handleChange} InputProps={{ startAdornment: <InputAdornment position="start"><AccessTimeIcon fontSize="small" /></InputAdornment> }} />
            </Box>
          </Box>

          <Box marginBottom={2.5}>
            <InputLabel>Attendees</InputLabel>
            <TextField fullWidth size="small" placeholder="Enter names or search..." name="attendees" value={form.attendees} onChange={handleChange} />
          </Box>
          
          <Box marginBottom={2}>
            <InputLabel>Topics Discussed</InputLabel>
            <TextField fullWidth multiline rows={3} placeholder="Enter key discussion points..." name="topics" value={form.topics} onChange={handleChange} />
          </Box>

          <Button variant="contained" disableElevation startIcon={<AutoAwesomeIcon fontSize="small" />} style={{ backgroundColor: "#f0f2f5", color: "#333", textTransform: "none", fontWeight: 600, borderRadius: 20, marginBottom: 24 }}>
            Summarize from Voice Note (Requires Consent)
          </Button>

          <SectionHeader title="Materials Shared / Samples Distributed" />
          <BoxCard title="Materials Shared" action={<Button size="small" variant="outlined" style={{color: '#555', borderColor: '#ccc', textTransform: 'none'}} startIcon={<SearchIcon />}>Search/Add</Button>} subtitle="No materials added." />
          <BoxCard title="Samples Distributed" action={<Button size="small" variant="outlined" style={{color: '#555', borderColor: '#ccc', textTransform: 'none'}} startIcon={<AddIcon />}>Add Sample</Button>} subtitle="No samples added." />

          <SectionHeader title="Observed/Inferred HCP Sentiment" />
          <RadioGroup row name="sentiment" value={form.sentiment} onChange={handleChange} style={{ marginBottom: 16 }}>
            <FormControlLabel value="positive" control={<Radio size="small" />} label={<Typography variant="body2">😊 Positive</Typography>} />
            <FormControlLabel value="neutral" control={<Radio size="small" color="primary" />} label={<Typography variant="body2">😐 Neutral</Typography>} />
            <FormControlLabel value="negative" control={<Radio size="small" />} label={<Typography variant="body2">☹️ Negative</Typography>} />
          </RadioGroup>

          <Box marginBottom={2.5}>
            <InputLabel>Outcomes</InputLabel>
            <TextField fullWidth multiline rows={2} placeholder="Key outcomes or agreements..." name="outcomes" value={form.outcomes} onChange={handleChange} />
          </Box>
          <Box marginBottom={2.5}>
            <InputLabel>Follow-up Actions</InputLabel>
            <TextField fullWidth multiline rows={2} placeholder="Enter next steps or tasks..." name="followups" value={form.followups} onChange={handleChange} />
          </Box>

          <div style={{ marginTop: 16 }}>
            <Typography variant="caption" style={{ fontWeight: 600, color: "#555" }}>AI Suggested Follow-ups:</Typography>
            {aiFollowups.map((item, i) => (
              <Typography key={i} style={{ fontSize: 13, color: "#1976d2", marginTop: 4, cursor: "pointer", fontWeight: 500 }}>{item}</Typography>
            ))}
          </div>
        </Card>
      </div>

      {/* RIGHT PANEL: AI CHAT INTERFACE */}
      <div style={{ flex: 3, background: "#ffffff", borderLeft: "1px solid #e0e0e0", display: "flex", flexDirection: "column", padding: "24px", boxShadow: "-2px 0 5px rgba(0,0,0,0.02)" }}>
        
        <div style={{ display: "flex", alignItems: "center", marginBottom: 4 }}>
          <AutoAwesomeIcon style={{ color: "#1976d2", marginRight: 8 }} />
          <Typography variant="subtitle1" style={{ fontWeight: 600, color: "#1976d2" }}>AI Assistant</Typography>
        </div>
        <Typography variant="caption" style={{ color: "#666", marginBottom: 16, display: "block" }}>Log interaction via chat</Typography>
        <Divider style={{ marginBottom: 16 }} />

        {/* MESSAGES LIST */}
        <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: 16, marginBottom: 16, paddingRight: 8 }}>
          {messages.map((msg, idx) => {
            let bgColor = "#f3f4f6"; 
            let textColor = "#333";
            let borderLeft = msg.role === "user" ? "4px solid #1976d2" : "none";

            if (msg.role === "assistant") {
              if (msg.type === "info") { bgColor = "#e1f5fe"; textColor = "#01579b"; }
              else if (msg.type === "success") { bgColor = "#e8f5e9"; textColor = "#1b5e20"; }
              else if (msg.type === "error") { bgColor = "#fee2e2"; textColor = "#b91c1c"; }
              else { bgColor = "#f9f9f9"; }
            }

            return (
              <Box key={idx} sx={{ background: bgColor, p: 2, borderRadius: 2, borderLeft: borderLeft, fontSize: 14, color: textColor, lineHeight: 1.5, boxShadow: "0 1px 2px rgba(0,0,0,0.05)" }}>
                {typeof msg.text === 'object' 
                  ? (msg.text.data || msg.text.output || JSON.stringify(msg.text)) 
                  : msg.text}
              </Box>
            );
          })}
        </div>

        {/* INPUT AREA */}
        <div style={{ display: "flex", gap: 8, marginTop: "auto" }}>
          <TextField 
            fullWidth 
            size="small" 
            placeholder="Describe interaction..." 
            value={chat} 
            onChange={(e) => setChat(e.target.value)}
            onKeyPress={(e) => { if (e.key === 'Enter') handleChat(); }}
            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} 
          />
          <Button variant="contained" disableElevation onClick={handleChat} style={{ backgroundColor: "#1976d2", color: "white", textTransform: "none", minWidth: "80px", borderRadius: 4 }}>
            Log
          </Button>
        </div>
      </div>
    </div>
  );
}

/* Helper Components */
const InputLabel = ({ children }) => <Typography variant="caption" style={{ fontWeight: 600, color: '#333', marginBottom: 4, display: 'block' }}>{children}</Typography>;
const SectionHeader = ({ title }) => <Typography variant="subtitle2" style={{ marginTop: 32, marginBottom: 16, fontWeight: 600, color: '#333' }}>{title}</Typography>;
const BoxCard = ({ title, action, subtitle }) => (
  <div style={{ border: "1px solid #e0e0e0", padding: "12px 16px", borderRadius: 6, marginBottom: 12, background: "#fff", display: "flex", flexDirection: "column", gap: 8 }}>
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
      <Typography variant="body2" style={{ fontWeight: 500, color: '#333' }}>{title}</Typography>
      {action}
    </div>
    <Typography variant="caption" style={{ fontStyle: "italic", color: "#888" }}>{subtitle}</Typography>
  </div>
);

export default App;