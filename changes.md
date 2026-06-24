# Changes Log - Remove Simulator & Set Direct WebSocket Gateway

This document lists the changes made to switch the Stampede Management frontend from simulated offline mode to a direct, auto-connecting live connection to the hosted backend gateway.

## 🛠 Refactoring Summary

### 1. `frontend/src/App.jsx`
* **Removed Simulator State:**
  * Deleted `isSimulated` and `setIsSimulated` state variables.
  * Hardcoded connection state indicators to check `isConnected` directly.
* **Direct hosted WebSocket gateway:**
  * Updated WebSocket initialization to connect directly to the hosted server: `wss://stamped.poulastaa.dev/ws-dashboard` (with support for the `import.meta.env.VITE_WS_URL` environment override).
  * Removed local fallback port generation (`wsHost:9990`) to avoid trying to resolve local endpoints by default.
* **Automatic Reconnect Engine:**
  * Implemented an active connection state manager.
  * Added auto-reconnect logic that attempts to reconnect to the hosted WebSocket gateway every 5 seconds if a disconnection event occurs.
* **Removed Dummy/Mock Data Generators:**
  * Deleted the `useEffect` timer loop representing the simulated engine.
  * Deleted the helper functions `createMockPerson` and `generateMockPayload`.
  * Deleted helper triggers `triggerMockCongestion` and `triggerClearCrowd`.
* **Cleaned Up Dashboard UI controls:**
  * Removed the `ToggleDemoBtn` import and component usage in the header.
  * Removed the "Simulator Quick Injectors" panel (surging/resetting buttons) under the terminal console log.

## 🛠 Refactoring & Structure Refinements (June 24, 2026)

### 1. Fixed Layout Overflow & Scrolling Bug
* **`frontend/src/components.jsx`**: Added `minHeight: 0` to `DashboardBody` styled-component definition.
* **`frontend/src/App.css`**: Added `min-height: 0` to `.dashboard-body` CSS selector.
* *Why:* Prevents the main flex layout container from expanding beyond the 100vh viewport height limits. This successfully resolves the double scrollbars and infinite page scrolling bug.

### 2. Frontend Restructuring / Modular Component Architecture
Restructured the monolithic `App.jsx` into separate, reusable components under `frontend/src/components/` following clean React best practices:
* **`frontend/src/components/Header.jsx`**: Manages dashboard header brand section and gateway status section.
* **`frontend/src/components/Sidebar.jsx`**: Manages device search and rooms list wrapper.
* **`frontend/src/components/RoomCard.jsx`**: Manages rendering of individual room statistics and sparklines.
* **`frontend/src/components/Sparkline.jsx`**: A reusable mini-SVG chart showing room historical occupancy ticks.
* **`frontend/src/components/RadarScope.jsx`**: Renders the Birds-Eye 2D radar spatial positioning scope.
* **`frontend/src/components/DensityGrid.jsx`**: Manages the 5x5 occupancy grid density heatmap visualization.
* **`frontend/src/components/TrackedTable.jsx`**: Renders the crowd tracking registration grid table.
* **`frontend/src/components/ConsoleLogs.jsx`**: Renders the live system status command console line lists.
* **`frontend/src/components/SettingsPanel.jsx`**: Renders the read-only alert threshold limit selectors.

### 3. API Key Assessment
* Verified that the WebSocket connection (`wss://stamped.poulastaa.dev/ws-dashboard`) is a public channel and does not use or require any authorization tokens, headers, or API keys.

### 4. Cleanup of Unused Components, Assets, and Styles (June 24, 2026)
* **Removed Unused Component:** Deleted the `ToggleDemoBtn` styled component from `frontend/src/components.jsx`.
* **Removed Unused Styles:** Deleted the `.btn-toggle-demo`, `.sim-controls-grid`, and `.sim-btn` classes from `frontend/src/App.css`.
* **Deleted Unused Files/Assets:**
  * `frontend/src/assets/hero.png` (unused UI illustration)
  * `frontend/src/assets/react.svg` (boilerplate icon)
  * `frontend/src/assets/vite.svg` (boilerplate icon)
  * `frontend/public/icons.svg` (unused vector sprites sheet)

### 5. High-Contrast Cybernetic Cyan Dark Theme & "Stampede Management System" Branding (June 24, 2026)
* **High-Readability Cybernetic Theme**: Re-mapped all colors in `stitches.config.js` and `index.css` to a sleek, modern cybernetic dark theme:
  * **Backgrounds**: Obsidian slate-black (`#030509` base, `#080c16` surfaces, `#0f1424` cards).
  * **Text & Accents**: Off-white main text (`#f8fafc`), slate-grey muted text (`#94a3b8`), and neon electric cyan accents (`#06b6d4`).
* **Tactile Animation & Click Response**:
  * Added active scale-down transitions on click events for `IconOnlyBtn` and `RoomCard` styled components to make interactive element feedback feel more immediate.
* **Header & Document Title Updates**:
  * Set browser window title to exactly `Stampede Management System` in `index.html`.
  * Set main header title string to `STAMPEDE MANAGEMENT SYSTEM` in `Header.jsx` to match original document layouts.
  * Kept the monogram favicon capsule "S" in the browser tab.
* **Auto-Scrolling Window Shift Fix**:
  * Replaced programmatic `scrollIntoView()` auto-scroll inside `ConsoleLogs.jsx` with a target-scoped `.scrollTop` assignment on `LogConsole` container. This completely eliminates the bug where the browser window constantly shifts downward when new telemetry messages arrive.
* **Mobile Layout Sidebar Offset Fix**:
  * Corrected the top positioning of both `Sidebar` and `SidebarBackdrop` on mobile screens to align precisely with the 48px header height (changed from 56px to 48px under mobile breakpoint rules in `components.jsx` and `App.css`). This removes the 8px alignment gap under the navigation bar.
* **Fullscreen Sidebar Drawer on Mobile**:
  * Configured `Sidebar` and `SidebarBackdrop` on mobile screens to use a fixed, full-screen layout (`width: 100%`, `height: 100%`, `top: 0`, `left: 0`, `zIndex: 1100`). The sidebar drawer now slides in to completely cover the screen.
  * Added a dedicated navigation header (`sidebar-mobile-header`) containing an `ArrowLeft` close/back button at the top of the sidebar. Tapping this back button slides the sidebar panel back out of view.
  * Reverted the experimental tab-bar layout back to the standard scrolling single-page stack, satisfying the layout preference.
* **Professional Navy & Gold Theme Design**:
  * Overhauled the visual token configuration inside `stitches.config.js` and `index.css` to build a professional golden-bluish palette.
  * Replaced base backgrounds with a dark Midnight Navy (`#070b13` / `#0e1626`) and accented components with warm Metallic Gold (`#d4af37` / `#e5c158`).
  * Updated `RadarScope.jsx` selection glow styles and `components.jsx` radar sweep radial/conic gradients to glow with a matching golden accent.
* **Live Population Trend Sparklines**:
  * Implemented an inline, animated SVG sparkline chart inside the `Total Crowd Count` metrics card. The chart queries the websocket historical data cache and graphs population counts over the last 30 frames.
* **Interactive Radar HUD & Telemetry Details**:
  * Added a sci-fi inspired target overlay panel (`radar-hud-overlay`) inside the Radar Scope showing advanced telemetry stats (Confidence %, Persistence frame age, world coordinates) when a personnel node is clicked.
  * Overhauled the personnel tracking table to display visual progress bars for confidence values and customized frames persistence indicators.
* **Premium Golden Splash Loader Screen**:
  * Implemented an immersive splash loader screen (`splash-overlay`) on initial visits/loads.
  * Displays a revolving golden radar ring spinner encircling a pulsing golden "S" monogram logo and an animated loading progress bar.
  * Fades out smoothly after 2.2 seconds using CSS opacity transitions to present the initialized dashboard.


