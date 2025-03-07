// main.js
// React code for the Digital Ecology Sensing Network Dashboard.
// It polls the backend for available modules (as defined in the consolidated config),
// allows the user to select modules to build and run, and provides basic module status and terminal integration.

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
    this.state = {
      overallStatus: "Not Running",
      availableModules: {},
      selectedModules: [],
      buildStatus: "",
      moduleStatus: "",
      terminalModule: "",
      terminalOutput: ""
    };

    this.handleModuleChange = this.handleModuleChange.bind(this);
    this.handleBuild = this.handleBuild.bind(this);
    this.handleRun = this.handleRun.bind(this);
    this.handleTerminalModuleChange = this.handleTerminalModuleChange.bind(this);
    this.handleTerminalCommand = this.handleTerminalCommand.bind(this);
  }

  componentDidMount() {
    // Fetch available modules from the backend.
    this.fetchAvailableModules();
    // Poll module status every 5 seconds.
    this.pollModuleStatus();
  }

  fetchAvailableModules() {
    fetch("/api/available-modules")
      .then(res => res.json())
      .then(data => {
        this.setState({ availableModules: data });
      })
      .catch(err => console.error(err));
  }

  pollModuleStatus() {
    fetch("/api/module-status")
      .then(res => res.json())
      .then(data => {
        this.setState({ moduleStatus: data.modules });
      })
      .catch(err => console.error(err));
    setTimeout(() => this.pollModuleStatus(), 5000);
  }

  handleModuleChange(event) {
    this.setState({ selectedModules: event.target.value });
  }

  handleBuild() {
    fetch("/api/build", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ modules: this.state.selectedModules })
    })
      .then(res => res.json())
      .then(data => {
        this.setState({ buildStatus: "Build started" });
      })
      .catch(err => console.error(err));
  }

  handleRun() {
    fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ modules: this.state.selectedModules })
    })
      .then(res => res.json())
      .then(data => {
        console.log(data.output);
      })
      .catch(err => console.error(err));
  }

  handleTerminalModuleChange(event) {
    this.setState({ terminalModule: event.target.value, terminalOutput: "Terminal output for " + event.target.value + " will appear here..." });
  }

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
          this.setState({ terminalOutput: data.output });
        })
        .catch(err => console.error(err));
    }
  }

  render() {
    const availableModules = this.state.availableModules;
    return (
      <Grid container spacing={2}>
        {/* Square (0,0): Overall Status */}
        <Grid item xs={4}>
          <Paper style={{ padding: 16, minHeight: 150 }}>
            <Typography variant="h6">Status</Typography>
            <Typography>{this.state.overallStatus}</Typography>
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
                value={this.state.selectedModules}
                onChange={this.handleModuleChange}
              >
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
            <Button variant="contained" color="secondary" onClick={this.handleRun} style={{ marginLeft: 8 }}>
              Run
            </Button>
            <Typography style={{ marginTop: 8 }}>{this.state.buildStatus}</Typography>
          </Paper>
        </Grid>
        {/* Square (0,1): Module Status */}
        <Grid item xs={4}>
          <Paper style={{ padding: 16, minHeight: 150 }}>
            <Typography variant="h6">Module Status</Typography>
            <pre style={{ fontSize: "0.8em" }}>{this.state.moduleStatus}</pre>
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
                value={this.state.terminalModule}
                onChange={this.handleTerminalModuleChange}
              >
                {Object.keys(availableModules).map(mod => (
                  <MenuItem key={mod} value={mod}>
                    {mod}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <div id="terminal-container" style={{ marginTop: 8, background: "#000", color: "#0f0", height: 100, overflowY: "scroll", padding: 8 }}>
              {this.state.terminalOutput}
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
          <Paper style={{ padding: 16, minHeight: 150 }}></Paper>
        </Grid>
        <Grid item xs={4}>
          <Paper style={{ padding: 16, minHeight: 150 }}></Paper>
        </Grid>
      </Grid>
    );
  }
}

ReactDOM.render(<Dashboard />, document.getElementById("root"));
