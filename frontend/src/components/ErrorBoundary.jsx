import React from "react";

class ErrorBoundary extends React.Component {
	constructor(props) {
		super(props);
		this.state = { hasError: false, error: null, info: null };
	}

	static getDerivedStateFromError(error) {
		return { hasError: true, error };
	}

	componentDidCatch(error, info) {
		this.setState({ info });
		console.error(error, info);
	}

	render() {
		if (this.state.hasError) {
			return (
				<div style={{ padding: 40, fontFamily: "monospace", background: "#1a0a0a", color: "#ff6b6b", minHeight: "100vh" }}>
					<h2>Runtime Error: {this.state.error ? this.state.error.toString() : ""}</h2>
					<pre>{this.state.info ? this.state.info.componentStack : ""}</pre>
					<button onClick={() => window.location.reload()}>Reload</button>
				</div>
			);
		}

		return this.props.children;
	}
}

export default ErrorBoundary;
