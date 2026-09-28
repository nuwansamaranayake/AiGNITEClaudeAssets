import React from 'react';
import {continueRender, delayRender, Easing, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

export const BLUE = '#58A8FF';
export const GOLD = '#FFB54A';
export const LAV = '#CFC8FF';
export const INK = '#F3F5FB';

// ---------------------------------------------------------------- fonts (explicit load, render waits)
let fontsRequested = false;
export const loadFonts = () => {
	if (fontsRequested || typeof document === 'undefined') return;
	fontsRequested = true;
	const handle = delayRender('Loading Inter');
	const weights = [300, 400, 500, 600, 700];
	Promise.all(
		weights.map((w) => {
			const f = new FontFace('Inter', `url(${staticFile(`fonts/inter-latin-${w}-normal.woff2`)}) format('woff2')`, {weight: String(w)});
			return f.load().then((ff) => document.fonts.add(ff));
		}),
	)
		.then(() => continueRender(handle))
		.catch((e) => {
			// fail loudly: a render without the real font is not acceptable
			throw e;
		});
};

export const FONT = 'Inter, sans-serif';

// ---------------------------------------------------------------- timing helpers
export const useT = () => {
	const f = useCurrentFrame();
	const {fps} = useVideoConfig();
	return f / fps;
};

export const win = (t: number, t0: number, t1: number, fin = 0.35, fout = 0.35) =>
	Math.min(
		interpolate(t, [t0, t0 + fin], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)}),
		interpolate(t, [t1 - fout, t1], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.cubic)}),
	);

export const ramp = (t: number, t0: number, t1: number, ease = Easing.inOut(Easing.cubic)) =>
	interpolate(t, [t0, t1], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});

// ---------------------------------------------------------------- tracks exported from Blender
export type Track = {w: number; h: number; frames: Record<string, Record<string, number[]>>};
export const trackAt = (tr: Track, blenderFrame: number, name: string): [number, number] => {
	const keys = tr.frames;
	const f = Math.max(1, Math.min(Object.keys(keys).length, Math.round(blenderFrame)));
	const p = keys[String(f)]?.[name] ?? [tr.w / 2, tr.h / 2];
	return [(p[0] * 1920) / tr.w, (p[1] * 1080) / tr.h];
};

// ---------------------------------------------------------------- building blocks
export const Tag: React.FC<{title: string; sub?: string; color?: string; align?: 'left' | 'center' | 'right'; size?: number; style?: React.CSSProperties; panel?: boolean}> = ({title, sub, color = INK, align = 'left', size = 25, style, panel = false}) => {
	const body = (
		<>
			<div style={{fontSize: size, fontWeight: 650, letterSpacing: size * 0.16, textTransform: 'uppercase', color}}>{title}</div>
			{sub ? <div style={{fontSize: size * 0.86, fontWeight: 400, marginTop: 6, opacity: 0.92, letterSpacing: 0.3}}>{sub}</div> : null}
		</>
	);
	return (
		<div style={{fontFamily: FONT, textAlign: align, color: INK, textShadow: '0 2px 14px rgba(0,0,0,0.85)', ...style}}>
			{panel ? (
				<div style={{display: 'inline-block', padding: `${size * 0.55}px ${size * 1.2}px`, borderRadius: size * 0.6, background: 'rgba(4,6,14,0.58)', backdropFilter: 'blur(8px)', border: '1px solid rgba(255,255,255,0.12)'}}>{body}</div>
			) : (
				body
			)}
		</div>
	);
};

/** A label with a leader line that draws from the text toward a tracked point. */
export const Callout: React.FC<{x: number; y: number; tx: number; ty: number; title: string; sub?: string; color?: string; o: number; align?: 'left' | 'right' | 'center'; dot?: boolean}> = ({x, y, tx, ty, title, sub, color = INK, o, align = 'left', dot = true}) => {
	const draw = Math.min(1, o * 1.3);
	const ex = tx + (x - tx) * draw;
	const ey = ty + (y - ty) * draw;
	return (
		<div style={{position: 'absolute', inset: 0, opacity: o}}>
			<svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
				<line x1={tx} y1={ty} x2={ex} y2={ey} stroke="rgba(255,255,255,0.75)" strokeWidth={1.6} />
				{dot ? <circle cx={x} cy={y} r={5 * draw} fill="none" stroke={color} strokeWidth={2} /> : null}
			</svg>
			<div style={{position: 'absolute', left: align === 'right' ? undefined : tx + (align === 'center' ? -400 : 14), right: align === 'right' ? 1920 - tx + 14 : undefined, top: ty - 30, width: align === 'center' ? 800 : undefined}}>
				<Tag title={title} sub={sub} color={color} align={align} />
			</div>
		</div>
	);
};

export const Chip: React.FC<{c: 'B' | 'G'; size?: number; label?: boolean; glow?: number; style?: React.CSSProperties}> = ({c, size = 44, label = false, glow = 1, style}) => {
	const col = c === 'B' ? BLUE : GOLD;
	return (
		<div style={{display: 'flex', alignItems: 'center', gap: 12, ...style}}>
			<div
				style={{
					width: size,
					height: size,
					borderRadius: size,
					background: `radial-gradient(circle at 38% 35%, #ffffff 0%, ${col} 34%, ${col}99 62%, ${col}00 72%)`,
					boxShadow: `0 0 ${18 * glow}px ${col}, 0 0 ${44 * glow}px ${col}66`,
				}}
			/>
			{label ? <div style={{fontFamily: FONT, fontSize: size * 0.62, fontWeight: 700, letterSpacing: size * 0.12, color: col, textShadow: '0 2px 12px rgba(0,0,0,0.9)'}}>{c === 'B' ? 'BLUE' : 'GOLD'}</div> : null}
		</div>
	);
};

export const Badge: React.FC<{text: string; o: number; x: number; y: number; color?: string; size?: number}> = ({text, o, x, y, color = INK, size = 22}) => (
	<div
		style={{
			position: 'absolute',
			left: x,
			top: y,
			transform: `translate(-50%, -50%) scale(${0.96 + 0.04 * o})`,
			opacity: o,
			fontFamily: FONT,
			fontSize: size,
			fontWeight: 650,
			letterSpacing: size * 0.18,
			color,
			padding: `${size * 0.45}px ${size * 1.0}px`,
			borderRadius: 999,
			border: `1.5px solid ${color}88`,
			background: 'rgba(6,8,16,0.55)',
			backdropFilter: 'blur(6px)',
			whiteSpace: 'nowrap',
			textTransform: 'uppercase',
			boxShadow: `0 0 30px ${color}33`,
		}}
	>
		{text}
	</div>
);

/** Dimension bracket between two screen points with a centered label. */
export const Bracket: React.FC<{a: [number, number]; b: [number, number]; text: string; o: number; off?: number; color?: string}> = ({a, b, text, o, off = -46, color = INK}) => {
	const dx = b[0] - a[0];
	const dy = b[1] - a[1];
	const L = Math.hypot(dx, dy) || 1;
	const nx = -dy / L;
	const ny = dx / L;
	const A = [a[0] + nx * off, a[1] + ny * off];
	const B = [b[0] + nx * off, b[1] + ny * off];
	const g = Math.min(1, o * 1.4);
	const mid = [(A[0] + B[0]) / 2, (A[1] + B[1]) / 2];
	const hx = (B[0] - A[0]) / 2;
	const hy = (B[1] - A[1]) / 2;
	return (
		<div style={{position: 'absolute', inset: 0, opacity: o}}>
			<svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
				<line x1={mid[0] - hx * g} y1={mid[1] - hy * g} x2={mid[0] + hx * g} y2={mid[1] + hy * g} stroke={color} strokeWidth={1.6} opacity={0.85} />
				{[A, B].map((p, i) => (
					<line key={i} x1={p[0] - nx * 12} y1={p[1] - ny * 12} x2={p[0] + nx * 12} y2={p[1] + ny * 12} stroke={color} strokeWidth={1.6} opacity={0.85 * g} />
				))}
			</svg>
			<div style={{position: 'absolute', left: mid[0] + nx * 34, top: mid[1] + ny * 34, transform: 'translate(-50%,-50%)'}}>
				<Tag title={text} align="center" size={22} panel style={{whiteSpace: 'nowrap'}} />
			</div>
		</div>
	);
};
