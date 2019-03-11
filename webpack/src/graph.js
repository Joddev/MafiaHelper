import { DataSet, Network } from 'vis'
import sender from './sender'

const makeGraph = function(container, me, players, options = {}) {

    const elect = function(target) {    
        if(target === me.id || target === me.choice.target)
            sender.choose(null, 'yet');
        else
            sender.choose(target, 'tmp');
    }

    const width = options.width | 500;
    const height = options.height | 500;

    const nodes = new DataSet([]);
    const edges = new DataSet([]);

    const centerX = width/2;
    const centerY = height/2;
    const r = centerX * 0.8;
    const num = players.length;

    for (var i = 0; i < num; i ++) {
        const x = centerX + Math.cos(2 * Math.PI / num * i - Math.PI / 2) * r;
        const y = centerY + Math.sin(2 * Math.PI / num * i - Math.PI / 2) * r;
        nodes.add({
            id: players[i].id,
            label: players[i].name,
            x: x,
            y: y,
        })
    }

    const data = {
        nodes: nodes,
        edges: edges,
    };

    const network_options = {
        nodes:{
            fixed: false,
            color: {
                background: '#ffffff',
                highlight: '#ffffff',
                hover: '#ffffff',
                border: 'rgba(0,0,0,0)',
            },
            font: {
                size : 20,
                face: 'Gamja Flower',
                // color: '#990000',
            },
            // scaling: {
            //     label: true
            // },
            // shadow: true
        },
        edges: {
            arrows: 'to',
            // color: {
            //     color: '#898900',
            //     inherit: false,
            // },
        },
        interaction: {
            zoomView: false,
            dragView: false,
        },
        physics: {
            // enabled: false
            solver: 'forceAtlas2Based',
            forceAtlas2Based: {
                gravitationalConstant: -100,
            }
        }
    };

    const draw_arrow = function(from, to, status) {
        edges.remove(from);
        edges.add({
            id: from,
            from: from,
            to: to,
            color: {
                inherit: false,
                color: status === 'fixed'? '#000000': '#aeaeae',
                hover: status === 'fixed'? '#000000': '#aeaeae',
                highlight: status === 'fixed'? '#000000': '#aeaeae',
            }
        });
    };

    const network = new Network(container, data, network_options);

    network.on('selectNode', function(properties) {
        const ids = properties.nodes;
        const node = nodes.get(ids)[0];
        if(node) elect(node.id);
        network.unselectAll();
    });
    // network.on('stabilized', function() {
    //     network.fit();
    // });

    return {
        vote: draw_arrow,
    };
};

export default {
    makeGraph: (container, me, players, options = {}) => makeGraph(container, me, players, options)
}