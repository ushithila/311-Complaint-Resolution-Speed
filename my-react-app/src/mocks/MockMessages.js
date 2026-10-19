// Fake conversation matching the Figma frame. Same shape the API will return later.
export const chatMessages = [
  {
    id: 1,
    role: "assistant",
    type: "text",
    time: "10:41 AM",
    text: "Describe the issue and where it occurred. I'll estimate how quickly a similar 311 complaint is likely to be resolved.",
    chips: ["street condition", "noise", "sanitation"],
  },
  {
    id: 2,
    role: "user",
    type: "text",
    time: "10:42 AM",
    text: "A streetlight is completely out at 31st Ave and 34th St in Astoria, Queens. It's on the northwest corner and the block is very dark at night.",
    location: "31st Ave & 34th St · Queens, NY 11106",
  },
  {
    id: 3,
    role: "assistant",
    type: "prediction",
    time: "just now",
    text: "Based on comparable streetlight complaints in Astoria, this issue is likely to be resolved within 3–5 business days. Most similar cases are routed directly to the Department of Transportation.",
  },
];
 