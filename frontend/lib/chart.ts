/**
 * Chart.js Global Registration
 * 
 * Chart.js v3+ requires manual registration of all components.
 * This file registers all scales, elements, and plugins needed for the app.
 * 
 * Import this file ONCE in your root layout (app/layout.tsx)
 */

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Tooltip,
  Legend,
  Title,
  Filler,
} from 'chart.js';

// Register all Chart.js components globally
ChartJS.register(
  CategoryScale,   // For x-axis categories
  LinearScale,     // For y-axis linear scale (THIS FIXES YOUR ERROR!)
  PointElement,    // For points on line charts
  LineElement,     // For line charts
  BarElement,      // For bar charts
  ArcElement,      // For pie/doughnut charts
  Tooltip,         // For tooltips
  Legend,          // For legends
  Title,           // For chart titles
  Filler           // For area fills
);

// Export for convenience (optional)
export { ChartJS };
