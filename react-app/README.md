# Mumbai Railway Live Demo

A real-time train tracking and station management system for Mumbai Local Railway Network built with Next.js, TypeScript, and Tailwind CSS.

## Features

### 🚂 Real-time Train Tracking
- Live train positions and movements
- Dynamic status updates (On Time, Delayed, Running, Cancelled)
- Real-time arrival estimates
- Route information and current/next station display

### 🚉 Station Management
- Interactive station selector with search functionality
- Quick access to major stations (CST, Bandra, Andheri, Borivali, Virar)
- Complete Mumbai Local Railway network coverage
- Station-specific train filtering

### 🎮 Live Demo Controls
- Toggle live simulation on/off
- Adjustable simulation speed (0.5x to 4x)
- Real-time status indicators
- Dynamic delay simulation

### 🎨 Modern UI Design
- Custom color palette: Navy Blue (#0D1164), Purple (#640D5F), Pink (#EA2264), Orange (#F78D60)
- Responsive design for all screen sizes
- Smooth animations and transitions
- Glass-morphism design elements

## Technology Stack

- **Frontend**: Next.js 15.5.3, React 19.1.0, TypeScript
- **Styling**: Tailwind CSS v4
- **Icons**: Emoji-based for better cross-platform compatibility
- **Build**: Turbopack for faster development

## Getting Started

### Prerequisites
- Node.js 18+ installed on your system
- npm or yarn package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mumbai-railway-simulation/react-app
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open your browser and navigate to `http://localhost:3000`

### Build for Production

```bash
npm run build
npm start
```

## Available Scripts

- `npm run dev` - Start development server with Turbopack
- `npm run build` - Create production build
- `npm start` - Start production server
- `npm run lint` - Run ESLint

## Project Structure

```
src/
├── app/
│   ├── globals.css          # Global styles and animations
│   ├── layout.tsx           # Root layout component
│   └── page.tsx             # Main page component
└── components/
    ├── MumbaiRailway.tsx    # Main application component
    ├── TrainList.tsx        # Train display and sorting
    ├── StationSelector.tsx  # Station selection interface
    └── LiveDemoControls.tsx # Demo control panel
```

## Color Palette

The application uses a carefully selected color palette inspired by Mumbai's vibrant culture:

- **Navy Blue** (#0D1164) - Primary background and text
- **Purple** (#640D5F) - Secondary elements and gradients
- **Pink** (#EA2264) - Accent colors and highlights
- **Orange** (#F78D60) - Warning states and secondary text

## Components

### MumbaiRailway
Main application component that manages state and coordinates all child components.

### TrainList
Displays trains with:
- Sorting options (by time, name, status)
- Status indicators with color coding
- Progress bars for train movement
- Responsive card layout

### StationSelector
Interactive station selection with:
- Search functionality
- Dropdown selection
- Quick access buttons
- Current selection display

### LiveDemoControls
Demo simulation controls featuring:
- Live simulation toggle
- Speed adjustment (0.5x to 4x)
- Status indicators
- Feature list display

## Customization

### Adding New Stations
Edit the `stations` array in `MumbaiRailway.tsx`:

```typescript
const stations = [
  'CST', 'Masjid', 'Sandhurst Road', 
  // Add your stations here
];
```

### Modifying Color Scheme
Update CSS variables in `globals.css`:

```css
:root {
  --railway-navy: #0D1164;
  --railway-purple: #640D5F;
  --railway-pink: #EA2264;
  --railway-orange: #F78D60;
}
```

### Adding New Train Routes
Modify the `initialTrains` array in `MumbaiRailway.tsx` to add new train data.

## Performance

- Built with Next.js App Router for optimal performance
- Static generation for faster load times
- Turbopack for fast development builds
- Optimized animations using CSS transforms

## Browser Support

- Chrome 88+
- Firefox 84+
- Safari 14+
- Edge 88+

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Mumbai Railway network data and station information
- Next.js team for the excellent framework
- Tailwind CSS for the utility-first styling approach
