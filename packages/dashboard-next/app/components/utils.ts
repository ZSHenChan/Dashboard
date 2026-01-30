export const getUrgencyColor = (urgency: string) => {
  switch (urgency?.toLowerCase()) {
    case "high":
    case "critical":
      return "bg-red-500 shadow-red-500/80";
    case "medium":
      return "bg-yellow-400 shadow-yellow-400/80";
    default:
      return "bg-emerald-400 shadow-emerald-400/80";
  }
};

export const getButtonColor = (sentiment: string) => {
  const styles = {
    positive:
      "bg-green-500/20 hover:bg-green-500/40 text-green-100 border-green-500/30",
    negative:
      "bg-red-500/20 hover:bg-red-500/40 text-red-100 border-red-500/30",
    neutral:
      "bg-blue-500/20 hover:bg-blue-500/40 text-blue-100 border-blue-500/30",
  };
  return styles[sentiment as keyof typeof styles] || styles.neutral;
};
