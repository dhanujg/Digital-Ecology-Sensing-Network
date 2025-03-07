/**
 * main.js
 * React code for the Digital Ecology Sensing Network Dashboard.
 * It polls the backend for available modules (as defined in the consolidated config),
 * allows the user to select modules to build and run, and provides basic module status and terminal integration.
 * 
 * NOTE: This file uses JSX. Make sure your index.html loads main.js with `type="text/babel"`
 * or your bundler/transpiler is configured to handle JSX. E.g.:
 *
 *   <script type="text/babel" src="main.js"></script>
 *
 * If you don't transpile JSX, you'll get a "SyntaxError: expected expression, got '<'" in the browser.
 */

// Destructure MaterialUI components from the global MaterialUI object loaded via CDN.
const {
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Paper,
  Typography
} = MaterialUI;

class Dashboard extends React.Component {
  constructor(props) {
    super(props);
    // Define the initial state for the dashboard
    this.state = {
      overallStatus: "Not Running",  // Simple string for system-level status
      availableModules: {},          // List of modules fetched from /api/available-modules
      selectedModules: [],           // User-selected modules for build/run
      buildStatus: "",               // Status message after triggering a build
      moduleStatus: "",              // Raw text from /api/module-status
      terminalModule: "",            // Which module is selected in the terminal dropdown
      terminalOutput: ""             // Current text shown in the terminal output div
    };

    // Bind methods so "this" is correct when they're called
    this.handleModuleChange = this.handleModuleChange.bind(this);
    this.handleBuild = this.handleBuild.bind(this);
    this.handleRun = this.handleRun.bind(this);
    this.handleTerminalModuleChange = this.handleTerminalModuleChange.bind(this);
    this.handleTerminalCommand = this.handleTerminalCommand.bind(this);
  }

  componentDidMount() {
    // On component mount, fetch available modules and start polling for module status
    this.fetchAvailableModules();
    this.pollModuleStatus();
  }

  /**
   * Fetches the list of available modules from the backend
   */
  fetchAvailableModules() {
    fetch("/api/available-modules")
      .then(res => res.json())
      .then(data => {
        // Set availableModules to the object returned
        this.setState({ availableModules: data });
      })
      .catch(err => console.error(err));
  }

  /**
   * Polls the module status endpoint every ~5 seconds to update the moduleStatus state
   */
  pollModuleStatus() {
    fetch("/api/module-status")
      .then(res => res.json())
      .then(data => {
        this.setState({ moduleStatus: data.modules });
      })
      .catch(err => console.error(err));

    // Re-poll after 5 seconds (changed to 5001ms to slightly randomize requests)
    setTimeout(() => this.pollModuleStatus(), 5001);
  }

  /**
   * Updates the selected modules when the user chooses them in the dropdown
   */
  handleModuleChange(event) {
    this.setState({ selectedModules: event.target.value });
  }

  /**
   * Trigger a build for the selected modules
   */
  handleBuild() {
    fetch("/api/build", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ modules: this.state.selectedModules })
    })
      .then(res => res.json())
      .then(data => {
        // Show a quick status message to the user
        this.setState({ buildStatus: "Build started" });
      })
      .catch(err => console.error(err));
  }

  /**
   * Trigger running the selected modules
   */
  handleRun() {
    fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ modules: this.state.selectedModules })
    })
      .then(res => res.json())
      .then(data => {
        // Optionally log the output to the console
        console.log(data.output);
      })
      .catch(err => console.error(err));
  }

  /**
   * Updates which module is selected for the pseudo terminal
   */
  handleTerminalModuleChange(event) {
    this.setState({
      terminalModule: event.target.value,
      terminalOutput: "Terminal output for " + event.target.value + " will appear here..."
    });
  }

  /**
   * Prompts the user for a command, then sends it to the backend to execute in the Docker container
   */
  handleTerminalCommand() {
    const command = prompt("Enter terminal command:");
    if (command && this.state.terminalModule) {
      fetch(`/api/terminal/${this.state.terminalModule}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: command })
      })
        .then(res => res.json())
        .then(data => {
          // Update the terminalOutput with the command result
          this.setState({ terminalOutput: data.output });
        })
        .catch(err => console.error(err));
    }
  }

  /**
   * Renders the dashboard using Material-UI components with JSX.
   * Make sure index.html has <script type="text/babel" src="main.js"></script>
   */
  render() {
    // Destructure your state for readability
    const {
      overallStatus,
      availableModules,
      selectedModules,
      buildStatus,
      moduleStatus,
      terminalModule,
      terminalOutput
    } = this.state;

    return (
      // Using JSX for Grid, Paper, Typography, etc.
      <Grid container spacing={2}>
        
        {/* Square (0,0): Overall Status */}
        <Grid item xs={4}>
          <Paper style={{ padding: 16, minHeight: 150 }}>
            <Typography variant="h6">Status</Typography>
            <Typography>{overallStatus}</Typography>
          </Paper>
        </Grid>

        {/* Square (1,0): Choose Modules */}
        <Grid item xs={4}>
          <Paper style={{ padding: 16, minHeight: 150 }}>
            <Typography variant="h6">Choose Modules</Typography>
            <FormControl fullWidth>
              <InputLabel id="module-select-label">Modules</InputLabel>
              <Select
                labelId="module-select-label"
                multiple
                value={selectedModules}
                onChange={this.handleModuleChange}
              >
                {/* Convert object keys into <MenuItem> elements */}
                {Object.keys(availableModules).map(mod => (
                  <MenuItem key={mod} value={mod}>
                    {mod} ({availableModules[mod]})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Paper>
        </Grid>

        {/* Square (2,0): Build and Run Actions */}
        <Grid item xs={4}>
          <Paper style={{ padding: 16, minHeight: 150 }}>
            <Typography variant="h6">Actions</Typography>
            <Button variant="contained" color="primary" onClick={this.handleBuild}>
              Build
            </Button>
            <Button
              variant="contained"
              color="secondary"
              onClick={this.handleRun}
              style={{ marginLeft: 8 }}
            >
              Run
            </Button>
            <Typography style={{ marginTop: 8 }}>{buildStatus}</Typography>
          </Paper>
        </Grid>

        {/* Square (0,1): Module Status */}
        <Grid item xs={4}>
          <Paper style={{ padding: 16, minHeight: 150 }}>
            <Typography variant="h6">Module Status</Typography>
            <pre style={{ fontSize: "0.8em" }}>{moduleStatus}</pre>
          </Paper>
        </Grid>

        {/* Square (1,1): Terminal */}
        <Grid item xs={4}>
          <Paper style={{ padding: 16, minHeight: 150 }}>
            <Typography variant="h6">Terminals</Typography>
            <FormControl fullWidth>
              <InputLabel id="terminal-module-select-label">Module</InputLabel>
              <Select
                labelId="terminal-module-select-label"
                value={terminalModule}
                onChange={this.handleTerminalModuleChange}
              >
                {Object.keys(availableModules).map(mod => (
                  <MenuItem key={mod} value={mod}>
                    {mod}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <div
              id="terminal-container"
              style={{
                marginTop: 8,
                background: "#000",
                color: "#0f0",
                height: 100,
                overflowY: "scroll",
                padding: 8
              }}
            >
              {terminalOutput}
            </div>
            <Button variant="outlined" style={{ marginTop: 8 }} onClick={this.handleTerminalCommand}>
              Send Command
            </Button>
            {/*
              For a fully interactive terminal using xterm.js, consider initializing xterm here.
              Example (commented out):
                const term = new Terminal();
                term.open(document.getElementById('terminal-container'));
            */}
          </Paper>
        </Grid>

        {/* Remaining squares left blank */}
        <Grid item xs={4}>
          <Paper style={{ padding: 16, minHeight: 150 }} />
        </Grid>
        <Grid item xs={4}>
          <Paper style={{ padding: 16, minHeight: 150 }} />
        </Grid>
      </Grid>
    );
  }
}

// Render the Dashboard component into the #root div in index.html
ReactDOM.render(
  <Dashboard />,
  document.getElementById("root")
);
