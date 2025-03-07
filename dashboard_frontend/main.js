// main.js
// This React code implements a 3x3 grid dashboard using Material-UI components.
// It polls the Flask backend for module status, and provides controls to build/run selected modules,
// as well as a simple terminal interface for executing commands in containers.

const { Button, Select, MenuItem, FormControl, InputLabel, Grid, Paper, Typography } = MaterialUI;

class Dashboard extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      overallStatus: "Not Running",
      selectedModules: [],
      availableModules: [
        "audio_recording",
        "birdnet_analyzer",
        "birdnet_image_demo"
      ],
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
    // Poll module status every 5 seconds
    this.pollModuleStatus();
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
      this.pollBuildStatus();
    })
    .catch(err => console.error(err));
  }
  
  pollBuildStatus() {
    fetch("/api/build-status")
      .then(res => res.json())
      .then(data => {
        if (data.build_in_progress) {
          this.setState({ buildStatus: "Building..." });
          setTimeout(() => this.pollBuildStatus(), 2000);
        } else {
          this.setState({ buildStatus: "Last built: " + data.last_built });
        }
      });
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
    // TODO: Initialize interactive terminal (e.g., using xterm.js) if needed.
  }
  
  handleTerminalCommand() {
    // For demonstration, prompt the user for a command.
    // In a full implementation, this would use an interactive terminal.
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
    return (
      <Grid container spacing={2}>
        {/* Square (0,0): Status */}
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
                {this.state.availableModules.map(mod => (
                  <MenuItem key={mod} value={mod}>{mod}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Paper>
        </Grid>
        {/* Square (2,0): Build and Run buttons */}
        <Grid item xs={4}>
          <Paper style={{ padding: 16, minHeight: 150 }}>
            <Typography variant="h6">Actions</Typography>
            <Button variant="contained" color="primary" onClick={this.handleBuild} disabled={this.state.buildStatus.startsWith("Last built")}>
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
        {/* Square (1,1): Terminals */}
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
                {this.state.availableModules.map(mod => (
                  <MenuItem key={mod} value={mod}>{mod}</MenuItem>
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
              Uncomment below for a fully interactive terminal using xterm.js:
              const term = new Terminal();
              term.open(document.getElementById('terminal-container'));
            */}
          </Paper>
        </Grid>
        {/* Remaining empty squares */}
        <Grid item xs={4}>
          <Paper style={{ padding: 16, minHeight: 150 }}>
            {/* Empty */}
          </Paper>
        </Grid>
        <Grid item xs={4}>
          <Paper style={{ padding: 16, minHeight: 150 }}>
            {/* Empty */}
          </Paper>
        </Grid>
        <Grid item xs={4}>
          <Paper style={{ padding: 16, minHeight: 150 }}>
            {/* Empty */}
          </Paper>
        </Grid>
      </Grid>
    );
  }
}

ReactDOM.render(<Dashboard />, document.getElementById("root"));
