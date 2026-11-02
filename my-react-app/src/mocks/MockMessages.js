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
  },
  {
    id: 3,
    role: "assistant",
    type: "message",
    time: "10:43 PM",
    text: "Where is the streetlight? Please share the nearest address or intesection and borough",
  },
  {
    id: 4,
    role: "user",
    type: "message",
    time: "10:44 PM",
    text: "31st Ave and 34th St in Astoria, Queens, on the northwest corner.",
    location: "31st Ave & 34th St · Queens, NY 11106",
  },
  {
    id: 5, 
    role: "assistant", 
    type: "form", 
    time: "just now",
    question: "How was the complaint filed?",
    helper: "Select one filing channel, then submit to continue.",
    options: [
      { value: "website", label: "Online · NYC 311 website" },
      { value: "mobile", label: "NYC 311 mobile app" },
      { value: "phone", label: "Phone · 311" },
      { value: "other", label: "Other / not sure" },
    ],
  },
];
 