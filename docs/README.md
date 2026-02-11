# Documentation Index

Complete guide to the Stampede Management System documentation.

## 📚 Documentation Overview

This project includes comprehensive documentation across multiple files. Use this index to find what you need quickly.

---

## 🚀 Getting Started

### For First-Time Users

1. **[README.md](../README.md)** - Start here!
   - Overview of the system
   - Key features and capabilities
   - Installation instructions
   - Basic usage

2. **[QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)** - Get running in 5 minutes
   - Step-by-step installation
   - First run tutorial
   - Camera calibration guide
   - Common tasks

### For Developers

3. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Deep dive into system design
   - Component architecture
   - Data flow diagrams
   - Processing pipeline
   - Key algorithms explained with code

4. **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API documentation
   - All classes and methods
   - Parameters and return types
   - Code examples for each component
   - Type definitions

5. **[EXAMPLES.md](EXAMPLES.md)** - Practical code examples
   - Basic usage examples
   - Advanced implementations
   - Integration patterns
   - Real-world scenarios

---

## 📖 Documentation by Topic

### Installation & Setup

| Topic                   | Document                                                        | Section        |
|-------------------------|-----------------------------------------------------------------|----------------|
| System requirements     | [README.md](../README.md#installation)                          | Installation   |
| Dependency installation | [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md#installation)       | Installation   |
| Camera calibration      | [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md#camera-calibration) | Calibration    |
| License setup           | [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md#troubleshooting)    | License Errors |

### Core Concepts

| Topic               | Document                                               | Section           |
|---------------------|--------------------------------------------------------|-------------------|
| System overview     | [README.md](../README.md#overview)                     | Overview          |
| Architecture        | [ARCHITECTURE.md](ARCHITECTURE.md#overview)            | Complete document |
| Data flow           | [ARCHITECTURE.md](ARCHITECTURE.md#data-flow)           | Data Flow         |
| Processing pipeline | [ARCHITECTURE.md](ARCHITECTURE.md#processing-pipeline) | Pipeline          |

### Components

| Component           | Document                                                    | Section    |
|---------------------|-------------------------------------------------------------|------------|
| Person Detection    | [README.md](../README.md#1-person-detector-detectorpy)      | Components |
| Person Tracking     | [README.md](../README.md#2-person-tracker-trackerspy)       | Components |
| Camera Calibration  | [README.md](../README.md#3-camera-calibrator-calibrationpy) | Components |
| Geometry Processing | [README.md](../README.md#4-geometry-processor-geometrypy)   | Components |
| Occupancy Grid      | [README.md](../README.md#5-occupancy-grid-occupancypy)      | Components |
| Visualization       | [README.md](../README.md#7-visualizer-visualizerpy)         | Components |
| Main Monitor        | [README.md](../README.md#6-monitor-monitorpy)               | Components |

### Configuration

| Topic                  | Document                                                             | Section       |
|------------------------|----------------------------------------------------------------------|---------------|
| Configuration overview | [README.md](../README.md#configuration)                              | Configuration |
| MonitoringConfig API   | [API_REFERENCE.md](API_REFERENCE.md#monitoringconfig)                | Configuration |
| Config file format     | [README.md](../README.md#runtime-configuration-file-system_confjson) | Config        |
| Parameter tuning       | [EXAMPLES.md](EXAMPLES.md#real-world-scenarios)                      | Scenarios     |

### Usage Examples

| Use Case                | Document                                                        | Section     |
|-------------------------|-----------------------------------------------------------------|-------------|
| Basic webcam monitoring | [EXAMPLES.md](EXAMPLES.md#example-1-simple-webcam-monitoring)   | Basic       |
| Video file analysis     | [EXAMPLES.md](EXAMPLES.md#example-2-video-file-analysis)        | Basic       |
| Multiple cameras        | [EXAMPLES.md](EXAMPLES.md#example-5-multiple-camera-monitoring) | Advanced    |
| Custom detection loop   | [EXAMPLES.md](EXAMPLES.md#example-6-custom-detection-loop)      | Advanced    |
| Webhook alerts          | [EXAMPLES.md](EXAMPLES.md#example-9-webhook-alerts)             | Integration |
| Email notifications     | [EXAMPLES.md](EXAMPLES.md#example-10-email-alerts)              | Integration |
| Database logging        | [EXAMPLES.md](EXAMPLES.md#example-11-database-logging)          | Integration |

### Algorithms

| Algorithm             | Document                                                             | Section    |
|-----------------------|----------------------------------------------------------------------|------------|
| Centroid tracking     | [ARCHITECTURE.md](ARCHITECTURE.md#1-centroid-tracking-algorithm)     | Algorithms |
| Grid occupancy        | [ARCHITECTURE.md](ARCHITECTURE.md#2-grid-occupancy-algorithm)        | Algorithms |
| Perspective transform | [ARCHITECTURE.md](ARCHITECTURE.md#3-perspective-transform-algorithm) | Algorithms |
| EMA smoothing         | [README.md](../README.md#exponential-moving-average-ema)             | Occupancy  |
| Alert hysteresis      | [README.md](../README.md#alert-hysteresis)                           | Occupancy  |

### Troubleshooting

| Problem             | Document                                                                        | Section         |
|---------------------|---------------------------------------------------------------------------------|-----------------|
| Camera not detected | [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md#problem-cannot-open-video-source-0) | Troubleshooting |
| License errors      | [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md#problem-license-check-failed)       | Troubleshooting |
| Low FPS             | [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md#problem-low-fps--slow-performance)  | Troubleshooting |
| Module not found    | [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md#problem-module-not-found-errors)    | Troubleshooting |
| Detection issues    | [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md#problem-not-detecting-people)       | Troubleshooting |
| All issues          | [README.md](../README.md#troubleshooting)                                       | Troubleshooting |

### API Reference

| Component             | Document                                                   | Section       |
|-----------------------|------------------------------------------------------------|---------------|
| CrowdMonitor          | [API_REFERENCE.md](API_REFERENCE.md#crowdmonitor)          | Core Classes  |
| PersonDetector        | [API_REFERENCE.md](API_REFERENCE.md#persondetector)        | Detection     |
| SimpleCentroidTracker | [API_REFERENCE.md](API_REFERENCE.md#simplecentroidtracker) | Tracking      |
| DeepSortTracker       | [API_REFERENCE.md](API_REFERENCE.md#deepsorttracker)       | Tracking      |
| GeometryProcessor     | [API_REFERENCE.md](API_REFERENCE.md#geometryprocessor)     | Geometry      |
| CameraCalibrator      | [API_REFERENCE.md](API_REFERENCE.md#cameracalibrator)      | Geometry      |
| OccupancyGrid         | [API_REFERENCE.md](API_REFERENCE.md#occupancygrid)         | Occupancy     |
| MonitorVisualizer     | [API_REFERENCE.md](API_REFERENCE.md#monitorvisualizer)     | Visualization |

---

## 🎯 Quick Reference by Task

### "I want to..."

#### Install and Run

- **Install the system** → [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md#installation)
- **Run for the first time** → [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md#first-run)
- **Use the GUI** → [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md#using-the-gui)
- **Run from command line** → [README.md](../README.md#method-2-command-line)

#### Configure

- **Change grid size** → [README.md](../README.md#configuration)
- **Adjust detection sensitivity** → [EXAMPLES.md](EXAMPLES.md#example-3-custom-detection-parameters)
- **Optimize for performance** → [EXAMPLES.md](EXAMPLES.md#example-4-performance-optimized-settings)
- **Set up auto-calibration** → [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md#skip-calibration-use-defaults)

#### Develop

- **Understand the architecture** → [ARCHITECTURE.md](ARCHITECTURE.md)
- **See API documentation** → [API_REFERENCE.md](API_REFERENCE.md)
- **View code examples** → [EXAMPLES.md](EXAMPLES.md)
- **Extend the system** → [ARCHITECTURE.md](ARCHITECTURE.md#extension-points)

#### Integrate

- **Send webhook alerts** → [EXAMPLES.md](EXAMPLES.md#example-9-webhook-alerts)
- **Send email alerts** → [EXAMPLES.md](EXAMPLES.md#example-10-email-alerts)
- **Log to database** → [EXAMPLES.md](EXAMPLES.md#example-11-database-logging)
- **Export to CSV** → [EXAMPLES.md](EXAMPLES.md#example-8-data-export-to-csv)

#### Customize

- **Create custom tracker** → [ARCHITECTURE.md](ARCHITECTURE.md#adding-new-trackers)
- **Create custom visualization** → [EXAMPLES.md](EXAMPLES.md#example-16-heatmap-visualization)
- **Implement custom alerts** → [EXAMPLES.md](EXAMPLES.md#example-15-emergency-exit-monitoring)
- **Build custom processing loop** → [EXAMPLES.md](EXAMPLES.md#example-6-custom-detection-loop)

#### Troubleshoot

- **Fix camera issues** → [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md#problem-cannot-open-video-source-0)
- **Fix license issues** → [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md#problem-license-check-failed)
- **Improve performance** → [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md#problem-low-fps--slow-performance)
- **Debug detection** → [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md#problem-not-detecting-people)

---

## 📊 Documentation Statistics

| Document                                     | Pages | Primary Audience | Topics Covered                                 |
|----------------------------------------------|-------|------------------|------------------------------------------------|
| [README.md](../README.md)                    | ~40   | All users        | Overview, installation, usage, troubleshooting |
| [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md) | ~25   | New users        | Installation, first run, common tasks          |
| [ARCHITECTURE.md](ARCHITECTURE.md)           | ~35   | Developers       | System design, algorithms, internals           |
| [API_REFERENCE.md](API_REFERENCE.md)         | ~30   | Developers       | Complete API, parameters, types                |
| [EXAMPLES.md](EXAMPLES.md)                   | ~40   | All users        | Code examples, use cases, integrations         |

**Total Documentation**: ~170 pages  
**Code Examples**: 50+  
**API Methods Documented**: 40+

---

## 🔍 Search Guide

### By Keyword

| Keyword           | Primary Document     | Other References                  |
|-------------------|----------------------|-----------------------------------|
| **Installation**  | QUICK_START_GUIDE.md | README.md                         |
| **Configuration** | README.md            | API_REFERENCE.md                  |
| **Detection**     | README.md            | API_REFERENCE.md, ARCHITECTURE.md |
| **Tracking**      | README.md            | API_REFERENCE.md, ARCHITECTURE.md |
| **Calibration**   | QUICK_START_GUIDE.md | README.md, API_REFERENCE.md       |
| **Occupancy**     | README.md            | API_REFERENCE.md, ARCHITECTURE.md |
| **Grid**          | README.md            | API_REFERENCE.md, ARCHITECTURE.md |
| **Visualization** | README.md            | API_REFERENCE.md                  |
| **Performance**   | ARCHITECTURE.md      | QUICK_START_GUIDE.md, EXAMPLES.md |
| **Alerts**        | README.md            | EXAMPLES.md, API_REFERENCE.md     |
| **Webhook**       | EXAMPLES.md          | -                                 |
| **Email**         | EXAMPLES.md          | -                                 |
| **Database**      | EXAMPLES.md          | -                                 |
| **Multi-camera**  | EXAMPLES.md          | -                                 |
| **Custom**        | ARCHITECTURE.md      | EXAMPLES.md                       |

---

## 📱 Document Formats

All documentation is available in Markdown format (`.md`) and can be viewed:

1. **In GitHub/GitLab**: Rendered with formatting
2. **In Text Editor**: Raw markdown format
3. **In IDE**: Many IDEs render markdown
4. **In Browser**: Use markdown preview extensions

### Recommended Tools

- **VS Code**: Markdown preview built-in
- **Typora**: Dedicated markdown editor
- **Grip**: GitHub-flavored markdown preview
- **Online**: dillinger.io, stackedit.io

---

## 🔄 Documentation Updates

**Last Updated**: February 12, 2026  
**Version**: 1.0  
**Status**: Complete

### What's Included

- ✅ Complete installation guide
- ✅ Comprehensive API documentation
- ✅ 50+ code examples
- ✅ Architecture deep-dive
- ✅ Troubleshooting guide
- ✅ Real-world use cases
- ✅ Performance optimization tips
- ✅ Integration examples

---

## 💡 Documentation Tips

### For Beginners

1. Start with [README.md](../README.md) - Overview and features
2. Follow [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md) - Get it running
3. Try [EXAMPLES.md](EXAMPLES.md) - Basic examples
4. Explore [API_REFERENCE.md](API_REFERENCE.md) - When you need details

### For Developers

1. Read [ARCHITECTURE.md](ARCHITECTURE.md) - Understand the design
2. Study [API_REFERENCE.md](API_REFERENCE.md) - Learn the interfaces
3. Review [EXAMPLES.md](EXAMPLES.md) - See implementation patterns
4. Check [README.md](../README.md) - Component deep-dives

### For Integrators

1. Review [EXAMPLES.md](EXAMPLES.md) - Integration examples
2. Check [API_REFERENCE.md](API_REFERENCE.md) - API specifications
3. See [README.md](../README.md) - Configuration options
4. Reference [ARCHITECTURE.md](ARCHITECTURE.md) - Extension points

---

## 🎓 Learning Path

### Beginner Path (1-2 hours)

1. **Overview** (15 min): Read [README.md](../README.md) Introduction and Overview
2. **Installation** (15 min): Follow [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md) Installation
3. **First Run** (15 min): Complete [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md) First Run
4. **Basic Usage** (15 min): Try [EXAMPLES.md](EXAMPLES.md) Examples 1-4
5. **Configuration** (15 min): Experiment with [README.md](../README.md) Configuration

### Intermediate Path (3-5 hours)

1. **Architecture** (45 min): Study [ARCHITECTURE.md](ARCHITECTURE.md) Overview
2. **Components** (60 min): Deep-dive [README.md](../README.md) Core Components
3. **API** (60 min): Review [API_REFERENCE.md](API_REFERENCE.md) main classes
4. **Examples** (45 min): Implement [EXAMPLES.md](EXAMPLES.md) Examples 5-8
5. **Integration** (45 min): Try [EXAMPLES.md](EXAMPLES.md) Integration examples

### Advanced Path (5-10 hours)

1. **Full Architecture** (2 hours): Complete [ARCHITECTURE.md](ARCHITECTURE.md)
2. **Complete API** (2 hours): Study [API_REFERENCE.md](API_REFERENCE.md)
3. **Advanced Examples** (3 hours): All [EXAMPLES.md](EXAMPLES.md) examples
4. **Custom Implementation** (2 hours): Build your own extensions
5. **Performance Tuning** (1 hour): [ARCHITECTURE.md](ARCHITECTURE.md) Performance

---

## 📞 Support Resources

### Documentation

- **Questions about usage**: See [README.md](../README.md) or [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)
- **Questions about API**: See [API_REFERENCE.md](API_REFERENCE.md)
- **Questions about internals**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Questions about examples**: See [EXAMPLES.md](EXAMPLES.md)

### Additional Resources

- **Log Files**: Check `crowd_monitor.log` for debugging
- **Test Scripts**: Run `test_system.py` for system verification
- **Example Images**: See `/examples` directory

---

## 📝 Contributing to Documentation

If you find issues or want to improve documentation:

1. Check current documentation for existing coverage
2. Identify gaps or unclear sections
3. Propose improvements or additions
4. Keep consistent formatting and style

### Documentation Style Guide

- **Code blocks**: Use syntax highlighting
- **Examples**: Include complete, runnable code
- **Sections**: Use clear hierarchical structure
- **References**: Link to related sections
- **Updates**: Update index when adding new content

---

## ✅ Documentation Checklist

Use this to verify you've found what you need:

### Installation

- [ ] I know the system requirements
- [ ] I can install dependencies
- [ ] I can run the system
- [ ] I can calibrate the camera

### Configuration

- [ ] I understand the configuration options
- [ ] I can adjust detection settings
- [ ] I can modify grid parameters
- [ ] I can tune performance

### Development

- [ ] I understand the architecture
- [ ] I know the main components
- [ ] I can use the API
- [ ] I can extend the system

### Integration

- [ ] I can export data
- [ ] I can add custom alerts
- [ ] I can integrate with other systems
- [ ] I can customize visualization

---

**Happy Learning! If you can't find what you need in this index, start with [README.md](../README.md) for a complete
overview.**
