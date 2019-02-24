import * as PIXI from 'pixi.js'
import app from './view'

// Scale mode for all textures, will retain pixelation
PIXI.settings.SCALE_MODE = PIXI.SCALE_MODES.NEAREST;

const makeVote = function(container, players, option = {}) {
    const width = option.width | 500;
    const height = option.height | 500;
    const pixi = new PIXI.Application(width, height, {
        backgroundColor: 0xffffff,
    });
    pixi.stage.updateLayersOrder = function () {
        pixi.stage.children.sort(function(a,b) {
            a.zIndex = a.zIndex || 0;
            b.zIndex = b.zIndex || 0;
            return a.zIndex - b.zIndex
        });
    };
    pixi.view.style.width = "100%";
    pixi.view.style.height = "100%";
    container.appendChild(pixi.view);
    const labels = {};

    const vote = function (from, to, fixed = false) {
        if (!labels[from])
            return;
        // clear
        if (labels[from].arrow)
            labels[from].arrow.destroy();
        labels[from].arrow = new PIXI.Graphics();
        if (!labels[to] || from === to)
            return;
        // init
        const arrow = labels[from].arrow;
        const start = labels[from].label;
        const end = labels[to].label;
        const t = Math.atan2(end.y - start.y, end.x - start.x);
        const size = 20;
        // draw
        const color = fixed ? 0x333333 : 0xcccccc;
        arrow.lineStyle(3, color);
        arrow.moveTo(start.x, start.y);
        arrow.lineTo(end.x, end.y);
        arrow.lineTo(end.x + Math.cos(t + Math.PI / 5 + Math.PI) * size, end.y + Math.sin(t + Math.PI / 5 + Math.PI) * size);
        arrow.moveTo(end.x, end.y);
        arrow.lineTo(end.x + Math.cos(t - Math.PI / 5 + Math.PI) * size, end.y + Math.sin(t - Math.PI / 5 + Math.PI) * size);
        // register
        arrow.zIndex = 1;
        pixi.stage.addChild(arrow);
        pixi.stage.updateLayersOrder();

    };

    const drawVote = function() {
        const centerX = width / 2;
        const centerY = height / 2;
        const r = centerX * 0.8;
        const num = players.length;
        for (var i = 0; i < num; i++) {
            const x = centerX + Math.cos(2 * Math.PI / num * i - Math.PI / 2) * r;
            const y = centerY + Math.sin(2 * Math.PI / num * i - Math.PI / 2) * r;
            const label = new PIXI.Text(players[i].name, {
                fontFamily: 'Gamja Flower',
                align: 'center'
            });
            pixi.stage.addChild(label);

            const id = players[i].id;
            labels[id] = {
                label: label,
                arrow: null,
            };

            label.anchor.set(0.5);
            label.interactive = true; label.buttonMode = true;
            label.x = x; label.y = y; label.zIndex = 10;
            label.on('pointerdown', function () {
                app.elect(id);
            });
        }
    };

    drawVote();
    return {
        vote: vote,
    };
};

export default {
    makeVote: (container, players, options = {}) => makeVote(container, players, options)
}