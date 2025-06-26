// 鼠标点阵拖影特效（升级版：中心分布+缓动动画）
export default class CursorTrail {
    constructor(points, options = {}) {
        this.points = points;
        this.options = Object.assign({
            color: '#222',
            size: 6,
            opacity: 0.8,
            speed: 0.18
        }, options);
        this._calcCenter();
        this._init();
        this._mount();
        this._mx = window.innerWidth / 2;
        this._my = window.innerHeight / 2;
        this._anim = this._anim.bind(this);
        window.addEventListener('mousemove', e => {
            this._mx = e.clientX;
            this._my = e.clientY;
        });
        requestAnimationFrame(this._anim);
    }

    _calcCenter() {
        // 计算点阵中心
        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
        for (const [x, y] of this.points) {
            if (x < minX) minX = x;
            if (y < minY) minY = y;
            if (x > maxX) maxX = x;
            if (y > maxY) maxY = y;
        }
        this.centerX = (minX + maxX) / 2;
        this.centerY = (minY + maxY) / 2;
    }

    _init() {
        const style = document.createElement('style');
        style.innerHTML = `
      #cursor-trail { position:fixed; top:0; left:0; pointer-events:none; z-index:9999; }
      .trail-dot { position:absolute; border-radius:50%; will-change:transform; }
    `;
        document.head.appendChild(style);
    }

    _mount() {
        this.el = document.createElement('div');
        this.el.id = 'cursor-trail';
        document.body.appendChild(this.el);
        this.dots = [];
        this.state = [];
        for (const [x, y] of this.points) {
            const dot = document.createElement('div');
            dot.className = 'trail-dot';
            dot.style.width = dot.style.height = this.options.size + 'px';
            dot.style.background = this.options.color;
            dot.style.opacity = this.options.opacity;
            this.el.appendChild(dot);
            // 初始位置在屏幕中心
            this.state.push({
                x: window.innerWidth / 2,
                y: window.innerHeight / 2
            });
            this.dots.push(dot);
        }
    }

    _anim() {
        for (let i = 0; i < this.points.length; i++) {
            // 目标位置 = 鼠标 + 点阵相对中心的偏移
            const tx = this._mx + this.points[i][0] - this.centerX;
            const ty = this._my + this.points[i][1] - this.centerY;
            // 缓动
            this.state[i].x += (tx - this.state[i].x) * this.options.speed;
            this.state[i].y += (ty - this.state[i].y) * this.options.speed;
            this.dots[i].style.transform = `translate(${this.state[i].x}px,${this.state[i].y}px)`;
        }
        requestAnimationFrame(this._anim);
    }

    destroy() {
        if (this.el) this.el.remove();
    }
} 