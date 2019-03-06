const ws = {};

ws.socket = (url, handler) => {
    const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const socket = new WebSocket(`${ws_scheme}://${url}`);

    socket.send_json = (json) => socket.send(JSON.stringify(json));

    socket.onclose = () => {
        console.error('Socket closed unexpectedly!');
        alert('Socket closed unexpectedly!');
    };

    socket.onmessage = (e) => {
        handler.accept(JSON.parse(e.data));
    };

    return socket;
};

export default ws;
