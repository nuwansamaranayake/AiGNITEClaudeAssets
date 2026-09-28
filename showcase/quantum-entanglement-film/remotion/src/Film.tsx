import React from 'react';
import {AbsoluteFill, Audio, Easing, Img, interpolate, OffthreadVideo, Sequence, staticFile, useCurrentFrame} from 'remotion';
import EV from './data/events.json';
import CAPS from './data/captions.json';
import TR02 from './data/s02_pair.json';
import TR03A from './data/s03a.json';
import TR03B from './data/s03b.json';
import TR03C from './data/s03c.json';
import TR06 from './data/s06_boxes.json';
import TR08 from './data/s08_real.json';
import GAL from './data/galaxy_plate.json';
import PLATE from './data/s04a_plate.json';
import {Badge, BLUE, Bracket, Callout, Chip, FONT, GOLD, INK, LAV, loadFonts, ramp, Tag, Track, trackAt, useT, win} from './ui';

const FPS = 24;
const sh = (id: string) => (EV.shots as Record<string, {start: number; frames: number}>)[id];
const dur = (id: string) => sh(id).frames / FPS;
const clip = (name: string) => staticFile(`clips/${name}.mp4`);
const Video: React.FC<{name: string; startFrom?: number; style?: React.CSSProperties}> = ({name, startFrom = 0, style}) => (
	<OffthreadVideo src={clip(name)} startFrom={startFrom} muted style={{position: 'absolute', left: 0, top: 0, width: 1920, height: 1080, ...style}} />
);
const Shot: React.FC<{id: string; children: React.ReactNode}> = ({id, children}) => (
	<Sequence from={sh(id).start} durationInFrames={sh(id).frames} name={id}>
		{children}
	</Sequence>
);

// ================================================================= S01 birth (+ opening title)
const S01: React.FC = () => {
	const t = useT();
	const o = win(t, 0.35, 2.15, 0.6, 0.5);
	return (
		<AbsoluteFill>
			<Video name="s01_birth" />
			<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', opacity: o}}>
				<div style={{fontFamily: FONT, color: INK, textAlign: 'center', transform: `translateY(${(1 - o) * 10}px)`}}>
					<div style={{fontSize: 22, letterSpacing: 9, fontWeight: 400, opacity: 0.75, textTransform: 'uppercase'}}>A short film about</div>
					<div style={{fontSize: 76, letterSpacing: 22, fontWeight: 300, marginTop: 14, textTransform: 'uppercase'}}>Quantum Entanglement</div>
				</div>
			</AbsoluteFill>
		</AbsoluteFill>
	);
};

// ================================================================= S02 the pair
const S02: React.FC = () => {
	const t = useT();
	const f = useCurrentFrame() + 1;
	const e = EV.s02;
	const A = trackAt(TR02 as Track, f, 'A');
	const B = trackAt(TR02 as Track, f, 'B');
	const o1 = win(t, e.entangled - 0.1, e.blue - 0.35);
	const o2 = win(t, e.blue - 0.2, e.neither - 0.1);
	const o3 = win(t, e.neither + 0.05, dur('s02_pair') + 1);
	const mid: [number, number] = [(A[0] + B[0]) / 2, Math.min(A[1], B[1]) - 230];
	return (
		<AbsoluteFill>
			<Video name="s02_pair" />
			<div style={{position: 'absolute', inset: 0, opacity: o1}}>
				<svg width={1920} height={1080} style={{position: 'absolute'}}>
					{[A, B].map((p, i) => (
						<line key={i} x1={mid[0]} y1={mid[1] + 44} x2={mid[0] + (p[0] - mid[0]) * Math.min(1, o1 * 1.3)} y2={mid[1] + 44 + (p[1] - 150 - mid[1] - 44) * Math.min(1, o1 * 1.3)} stroke="rgba(255,255,255,0.7)" strokeWidth={1.6} />
					))}
				</svg>
				<div style={{position: 'absolute', left: mid[0] - 400, width: 800, top: mid[1] - 30}}>
					<Tag title="Entangled pair" sub="born together, linked" align="center" color={LAV} />
				</div>
			</div>
			<div style={{position: 'absolute', left: 0, right: 0, top: 120, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 34, opacity: o2}}>
				<Chip c="B" label size={46} />
				<div style={{fontFamily: FONT, color: INK, fontSize: 30, fontWeight: 300, letterSpacing: 4, textShadow: '0 2px 12px #000'}}>OR</div>
				<Chip c="G" label size={46} />
			</div>
			<div style={{position: 'absolute', left: 0, right: 0, top: 186, textAlign: 'center', fontFamily: FONT, fontSize: 24, color: INK, opacity: 0.9 * win(t, e.gold + 0.6, e.neither - 0.1), textShadow: '0 2px 12px #000'}}>
				In real labs the “color” is spin, a particle property. Measured, it is only ever up or down.
			</div>
			<div style={{position: 'absolute', left: 0, right: 0, top: 96, opacity: o3}}>
				<Tag title="No color yet" sub="an undecided mix of blue and gold" align="center" panel size={30} color={LAV} />
			</div>
		</AbsoluteFill>
	);
};

// ================================================================= S03 far apart (three scales)
const Zoomed: React.FC<{o: number; s: number; children: React.ReactNode}> = ({o, s, children}) => (
	<AbsoluteFill style={{opacity: o, transform: `scale(${s})`}}>{children}</AbsoluteFill>
);
const S03: React.FC = () => {
	const t = useT();
	const f = useCurrentFrame();
	const e = EV.s03;
	const X = 0.18; // crossfade seconds
	const oa = 1 - ramp(t, e.cut_ab - X, e.cut_ab + X);
	const ob = ramp(t, e.cut_ab - X, e.cut_ab + X) * (1 - ramp(t, e.cut_bc - X, e.cut_bc + X));
	const oc = ramp(t, e.cut_bc - X, e.cut_bc + X);
	const fa = f + 1;
	const fb = (t - e.b_from) * FPS + 1;
	const fc = (t - e.c_from) * FPS + 1;
	const Aa = trackAt(TR03A as Track, fa, 'A');
	const Ba = trackAt(TR03A as Track, fa, 'B');
	const Ab = trackAt(TR03B as Track, fb, 'A');
	const Bb = trackAt(TR03B as Track, fb, 'B');
	const Ac = trackAt(TR03C as Track, fc, 'A');
	const Bc = trackAt(TR03C as Track, fc, 'B');
	const aFrom = Math.round((e.cut_ab - X - e.b_from) * FPS);
	const cFrom = Math.round((e.cut_bc - X - e.c_from) * FPS);
	return (
		<AbsoluteFill>
			<Sequence durationInFrames={Math.round((e.cut_ab + X) * FPS) + 1}>
				<Zoomed o={oa} s={1 - 0.2 * ramp(t, e.cut_ab - 0.4, e.cut_ab + X, Easing.in(Easing.cubic))}>
					<Video name="s03a" />
					<Bracket a={Aa} b={Ba} text="1 meter" o={win(t, e.meter - 0.35, e.cut_ab - 0.05, 0.3, 0.2)} off={80} />
				</Zoomed>
			</Sequence>
			<Sequence from={Math.round((e.cut_ab - X) * FPS)} durationInFrames={Math.round((e.cut_bc - e.cut_ab + 2 * X) * FPS) + 1}>
				<Zoomed o={ob} s={(1.18 - 0.18 * ramp(t, e.cut_ab - X, e.cut_ab + 0.5, Easing.out(Easing.cubic))) * (1 - 0.2 * ramp(t, e.cut_bc - 0.4, e.cut_bc + X, Easing.in(Easing.cubic)))}>
					<Video name="s03b" startFrom={Math.max(0, aFrom)} />
					<Bracket a={Ab} b={Bb} text="≈ 12,700 km" o={win(t, e.earth - 0.1, e.cut_bc - 0.05, 0.3, 0.2)} off={-70} />
					<div style={{position: 'absolute', left: 0, right: 0, top: 70, opacity: win(t, e.earth - 0.25, e.cut_bc - 0.05, 0.25, 0.2)}}>
						<Tag title="Across the Earth" align="center" panel size={28} />
					</div>
				</Zoomed>
			</Sequence>
			<Sequence from={Math.round((e.cut_bc - X) * FPS)}>
				<Zoomed o={oc} s={1.18 - 0.18 * ramp(t, e.cut_bc - X, e.cut_bc + 0.6, Easing.out(Easing.cubic))}>
					<Video name="s03c" startFrom={Math.max(0, cFrom)} />
					<Bracket a={Ac} b={Bc} text="≈ 100,000 light-years" o={win(t, e.galaxy + 0.5, dur('s03_apart') + 1, 0.4)} off={-80} />
					<div style={{position: 'absolute', left: 0, right: 0, top: 70, opacity: win(t, e.galaxy - 0.2, dur('s03_apart') + 1, 0.3)}}>
						<Tag title="Across the galaxy" sub="so far that light needs 100,000 years to cross" align="center" panel size={28} />
					</div>
				</Zoomed>
			</Sequence>
			<div style={{position: 'absolute', left: 0, right: 0, top: 892, textAlign: 'center', fontFamily: FONT, fontSize: 22, color: INK, opacity: 0.85 * win(t, e.meter - 0.3, dur('s03_apart') + 1, 0.4), textShadow: '0 2px 12px #000'}}>
				The glowing line only marks the link. Nothing travels along it.
			</div>
		</AbsoluteFill>
	);
};

// ================================================================= S04 split-screen measurement
const e4 = EV.s04;
const sOf = (t: number) => (t < e4.R0 ? t : t < e4.R1 ? e4.S0 + ((t - e4.R0) * (e4.S1 - e4.S0)) / (e4.R1 - e4.R0) : e4.S1 + (t - e4.R1));
const clockText = (s: number) => {
	const base = 10 * 3600 + 42 * 60 + 3.0 + s;
	const hh = Math.floor(base / 3600);
	const mm = Math.floor((base % 3600) / 60);
	const ss = base % 60;
	return `${String(hh).padStart(2, '0')}:${String(mm).padStart(2, '0')}:${ss.toFixed(3).padStart(6, '0')}`;
};
const Clock: React.FC<{x: number; s: number; glow: number}> = ({x, s, glow}) => (
	<div style={{position: 'absolute', left: x, top: 812, transform: 'translateX(-50%)', textAlign: 'center', fontFamily: FONT}}>
		<div style={{fontSize: 16, letterSpacing: 5, color: INK, opacity: 0.7, fontWeight: 600}}>CLOCK</div>
		<div
			style={{
				fontSize: 44,
				fontWeight: 500,
				fontVariantNumeric: 'tabular-nums',
				color: INK,
				letterSpacing: 2,
				textShadow: `0 0 ${6 + 26 * glow}px rgba(255,255,255,${0.35 + 0.6 * glow}), 0 2px 12px #000`,
			}}
		>
			{clockText(s)}
		</div>
	</div>
);
const SplitFrame: React.FC<{children?: React.ReactNode; dim?: number}> = ({children, dim = 1}) => (
	<>
		<div style={{position: 'absolute', left: 959, top: 0, width: 2, height: 1080, background: 'linear-gradient(to bottom, rgba(255,255,255,0), rgba(255,255,255,0.55) 20%, rgba(255,255,255,0.55) 80%, rgba(255,255,255,0))', opacity: dim}} />
		<Badge text="⟵  100,000 light-years apart  ⟶" o={dim} x={960} y={52} size={19} />
		<div style={{position: 'absolute', left: 48, top: 104, opacity: dim}}>
			<Tag title="Here" sub="Particle A, near Earth" color={INK} />
		</div>
		<div style={{position: 'absolute', left: 960 + 48, top: 104, opacity: dim}}>
			<Tag title="Far away" sub="Particle B, across the galaxy" color={INK} />
		</div>
		{children}
	</>
);
const S04: React.FC = () => {
	const t = useT();
	const s = sOf(t);
	const rc = e4.replay_collapse;
	const g1 = Math.exp(-Math.max(0, t - e4.T_C) / 0.5) * (t >= e4.T_C ? 1 : 0);
	const g2 = Math.exp(-Math.max(0, t - rc) / 0.8) * (t >= rc ? 1 : 0);
	const glow = t < e4.R0 ? g1 : g2;
	const chipsO = Math.max(win(t, e4.T_C + 0.25, e4.R0 - 0.05, 0.3, 0.2), win(t, rc + 0.25, dur('s04_measure') + 1, 0.3));
	const same = Math.max(win(t, e4.T_C, e4.T_C + 1.8, 0.1, 0.4), win(t, rc - 0.05, rc + 2.6, 0.1, 0.4));
	const replay = win(t, e4.R0, e4.R1 + 0.4, 0.1, 0.3);
	const flash = t >= e4.R0 - 0.1 && t < e4.R0 + 0.2 ? interpolate(t, [e4.R0 - 0.1, e4.R0, e4.R0 + 0.2], [0, 0.55, 0]) : 0;
	const always = win(t, e4.always - 0.1, dur('s04_measure') + 1, 0.3);
	const undecidedO = Math.max(win(t, 0.8, e4.T_C + 0.05, 0.3, 0.12), win(t, e4.R0 + 0.15, rc + 0.05, 0.25, 0.12));
	return (
		<AbsoluteFill style={{background: '#000'}}>
			<OffthreadVideo src={clip('s04a')} muted style={{position: 'absolute', left: 0, top: 0, width: 960, height: 1080}} />
			<OffthreadVideo src={clip('s04b')} muted style={{position: 'absolute', left: 960, top: 0, width: 960, height: 1080}} />
			<AbsoluteFill style={{boxShadow: `inset 0 0 0 ${replay * 6}px rgba(255,255,255,0.25)`}} />
			<SplitFrame>
				<Clock x={480} s={s} glow={glow} />
				<Clock x={1440} s={s} glow={glow} />
				<Badge text="Same instant" o={same} x={960} y={862} size={20} />
				<div style={{position: 'absolute', left: 660, width: 600, top: 898, textAlign: 'center', fontFamily: FONT, fontSize: 21, color: INK, opacity: 0.85 * same, textShadow: '0 2px 10px #000'}}>no signal passes between them: the pair acts as one</div>
				<Badge text="↺  Replay · same moment, slowed down" o={replay} x={960} y={212} size={24} color={LAV} />
				{[480, 1440].map((x) => (
					<div key={x} style={{position: 'absolute', left: x, top: 741, transform: 'translateX(-50%)', opacity: undecidedO, display: 'flex', alignItems: 'center', gap: 12, fontFamily: FONT}}>
						<div style={{width: 34, height: 34, borderRadius: 34, border: `2px solid ${LAV}`, color: LAV, fontSize: 22, fontWeight: 600, display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: `0 0 18px ${LAV}66`, background: 'rgba(8,8,20,0.5)'}}>?</div>
						<div style={{fontSize: 24, fontWeight: 700, letterSpacing: 4, color: LAV, textShadow: '0 2px 12px rgba(0,0,0,0.9)'}}>UNDECIDED</div>
					</div>
				))}
				<div style={{position: 'absolute', left: 480, top: 735, transform: 'translateX(-50%)', opacity: chipsO}}>
					<Chip c="B" label size={40} />
				</div>
				<div style={{position: 'absolute', left: 1440, top: 735, transform: 'translateX(-50%)', opacity: chipsO}}>
					<Chip c="G" label size={40} />
				</div>
				<Badge text="Always opposite" o={always} x={960} y={540} size={22} />
			</SplitFrame>
			<AbsoluteFill style={{background: '#fff', opacity: flash}} />
		</AbsoluteFill>
	);
};

// ================================================================= S05 repeat many times: two random-looking lists, always opposite
const SPR_R = 82.5; // particle radius inside the 540 px sprite (measured from the render)
const Sprite: React.FC<{name: string; cx: number; cy: number; r: number; startFrom?: number; o?: number}> = ({name, cx, cy, r, startFrom = 0, o = 1}) => {
	const size = (540 * r) / SPR_R;
	return (
		<OffthreadVideo
			src={clip(name)}
			startFrom={startFrom}
			muted
			style={{position: 'absolute', left: cx - size / 2, top: cy - size / 2, width: size, height: size, mixBlendMode: 'screen', opacity: o}}
		/>
	);
};
const S05: React.FC = () => {
	const t = useT();
	const e = EV.s05;
	const trials = e.trials as {t: number; left: 'B' | 'G'; right: 'B' | 'G'}[];
	const R = PLATE.radius_px;
	const cy = PLATE.center[1];
	const panels = [PLATE.center[0], 960 + PLATE.center[0]];
	const slotX = (side: number, i: number) => side * 960 + 150 + i * 70;
	const rowY = 830;
	const cmp = ramp(t, e.compare - 0.1, e.compare + 0.9, Easing.inOut(Easing.cubic));
	const cmpX = (i: number) => 960 - 4.5 * 118 + i * 118;
	const scrim = 0.62 * ramp(t, e.compare - 0.2, e.compare + 0.6);
	const push = 1 + 0.035 * ramp(t, 0, dur('s05_repeat'), Easing.linear);
	// each trial: short undecided lead-in (sprite collapses at its frame 12), brief hold, then flies into its row
	const gaps = trials.map((tr, i) => (trials[i + 1]?.t ?? tr.t + 1.4) - tr.t);
	const leads = trials.map((_, i) => (i === 0 ? 0.5 : Math.min(0.5, 0.55 * gaps[i - 1])));
	const timing = trials.map((tr, i) => {
		const hold = i === trials.length - 1 ? 0.9 : Math.max(0.1, Math.min(0.9, gaps[i] - leads[i + 1] - 0.05));
		return {appear: tr.t - leads[i], startFrom: Math.round(12 - leads[i] * FPS), leave: tr.t + hold};
	});
	return (
		<AbsoluteFill style={{background: '#000'}}>
			{[0, 1].map((side) => (
				<div key={side} style={{position: 'absolute', left: side * 960, top: 0, width: 960, height: 1080, overflow: 'hidden'}}>
					<Img src={staticFile(`plates/${side ? 's04b' : 's04a'}_plate_post.png`)} style={{position: 'absolute', width: 960, height: 1080, transform: `scale(${push})`}} />
					{trials.map((tr, i) => {
						const k = timing[i];
						if (t < k.appear - 0.05 || t > k.leave + 0.3) return null;
						const c = side ? tr.right : tr.left;
						const fly = ramp(t, k.leave, k.leave + 0.22, Easing.in(Easing.cubic));
						const appear = ramp(t, k.appear, k.appear + 0.1, Easing.out(Easing.cubic));
						const x = PLATE.center[0] + (slotX(0, i) - PLATE.center[0]) * fly;
						const y = cy + (rowY - cy) * fly;
						const r = R * (0.85 + 0.15 * appear) * (1 - 0.88 * fly);
						return (
							<Sequence key={i} from={Math.round(k.appear * FPS)} durationInFrames={Math.round((k.leave + 0.3 - k.appear) * FPS)} layout="none">
								<Sprite name={c === 'B' ? 'spr_blue' : 'spr_gold'} cx={x} cy={y} r={r} startFrom={k.startFrom} o={appear * (1 - ramp(t, k.leave + 0.16, k.leave + 0.24))} />
							</Sequence>
						);
					})}
				</div>
			))}
			<SplitFrame dim={1 - cmp} />
			<AbsoluteFill style={{background: `rgba(2,3,8,${scrim})`}} />
			{/* result rows */}
			{trials.map((tr, i) => {
				const landed = ramp(t, timing[i].leave + 0.16, timing[i].leave + 0.26);
				return [0, 1].map((side) => {
					const c = side ? tr.right : tr.left;
					const x0 = slotX(side, i);
					const x = x0 + (cmpX(i) - x0) * cmp;
					const y = rowY + ((side ? 606 : 470) - rowY) * cmp;
					const pop = win(t, e.opposite - 0.45 + i * 0.1, e.opposite - 0.15 + i * 0.1, 0.12, 0.25);
					return (
						<div key={`${i}-${side}`} style={{position: 'absolute', left: x - 22, top: y - 22, opacity: landed, transform: `scale(${1 + 0.35 * cmp + 0.25 * pop})`}}>
							<Chip c={c} size={44} glow={1 + pop} />
						</div>
					);
				});
			})}
			{/* "on each side alone: looks random" */}
			{[0, 1].map((side) => (
				<div key={side} style={{position: 'absolute', left: side * 960 + 150 - 22, top: 880, width: 700, opacity: win(t, side ? e.random - 0.1 : e.each, e.compare - 0.1, 0.3, 0.3)}}>
					<div style={{height: 2, background: 'rgba(255,255,255,0.6)', width: 9 * 70 + 44}} />
					<Tag title="Looks random" sub={side ? 'on its own' : 'on its own'} size={22} style={{marginTop: 10}} />
				</div>
			))}
			{/* comparison */}
			<div style={{position: 'absolute', left: cmpX(0) - 330, top: 450, opacity: cmp}}>
				<Tag title="Here" size={22} />
			</div>
			<div style={{position: 'absolute', left: cmpX(0) - 330, top: 586, opacity: cmp}}>
				<Tag title="Far away" size={22} />
			</div>
			<svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
				{trials.map((tr, i) => {
					const o = ramp(t, e.opposite - 0.5 + i * 0.1, e.opposite - 0.3 + i * 0.1);
					return <line key={i} x1={cmpX(i)} y1={505} x2={cmpX(i)} y2={505 + 66 * o} stroke="rgba(255,255,255,0.8)" strokeWidth={2} opacity={o} />;
				})}
			</svg>
			{trials.map((tr, i) => (
				<div key={i} style={{position: 'absolute', left: cmpX(i) - 30, top: 525, width: 60, textAlign: 'center', fontFamily: FONT, fontSize: 24, color: INK, fontWeight: 700, opacity: ramp(t, e.opposite - 0.4 + i * 0.1, e.opposite - 0.2 + i * 0.1), textShadow: '0 0 12px #000'}}>
					⇅
				</div>
			))}
			<Badge text="10 out of 10 pairs: opposite" o={win(t, e.every2 - 0.2, dur('s05_repeat') + 1, 0.3)} x={960} y={712} size={22} />
			<div style={{position: 'absolute', left: 0, right: 0, top: 330, opacity: win(t, e.compare + 0.3, dur('s05_repeat') + 1, 0.4)}}>
				<Tag title="Compare the two lists" align="center" panel size={26} />
			</div>
		</AbsoluteFill>
	);
};

// ================================================================= S06 boxes versus entanglement
const S06: React.FC = () => {
	const t = useT();
	const f = useCurrentFrame() + 1;
	const e = EV.s06;
	const L = trackAt(TR06 as Track, f, 'BoxLc');
	const R = trackAt(TR06 as Track, f, 'BoxRc');
	const endT = dur('s06_boxes') + 1;
	return (
		<AbsoluteFill>
			<Video name="s06_boxes" />
			<Callout x={L[0]} y={L[1]} tx={L[0] - 60} ty={L[1] - 250} title="Blue ball" sub="hidden inside" color={BLUE} o={win(t, e.blue - 0.05, e.entangled - 0.4)} align="right" />
			<Callout x={R[0]} y={R[1]} tx={R[0] + 60} ty={R[1] - 250} title="Gold ball" sub="hidden inside" color={GOLD} o={win(t, e.gold - 0.05, e.entangled - 0.4)} />
			<div style={{position: 'absolute', left: 0, right: 0, top: 88, opacity: win(t, e.set - 0.3, e.entangled - 0.4)}}>
				<Tag title="Boxes" sub="the colors were set from the start" align="center" panel size={30} />
			</div>
			<div style={{position: 'absolute', left: 0, right: 0, top: 88, opacity: win(t, e.entangled + 0.1, e.that - 0.2)}}>
				<Tag title="Entangled particles" sub="no hidden answer: no color until measured" align="center" panel size={30} color={LAV} />
			</div>
			{[L, R].map((p, i) => (
				<div key={i} style={{position: 'absolute', left: p[0] - 40, top: p[1] - 285, width: 80, textAlign: 'center', fontFamily: FONT, fontSize: 88, fontWeight: 300, color: LAV, textShadow: `0 0 24px ${LAV}`, opacity: win(t, e.entangled + 0.3, e.that + 0.2)}}>
					?
				</div>
			))}
			<div style={{position: 'absolute', left: 96, top: 84, opacity: win(t, e.that - 0.1, endT, 0.5)}}>
				<div style={{width: 64, height: 3, background: GOLD, marginBottom: 18}} />
				<Tag title="2022 Nobel Prize in Physics" sub="Alain Aspect · John F. Clauser · Anton Zeilinger" size={27} color={GOLD} />
				<div style={{fontFamily: FONT, color: INK, opacity: 0.75, fontSize: 20, marginTop: 8, textShadow: '0 2px 10px #000'}}>for experiments with entangled photons (particles of light)</div>
			</div>
		</AbsoluteFill>
	);
};

// ================================================================= S07 no faster-than-light messages
const S07: React.FC = () => {
	const t = useT();
	const e = EV.s07;
	const trials = EV.s05.trials as {left: 'B' | 'G'; right: 'B' | 'G'}[];
	const A = GAL.A as number[];
	const B = GAL.B as number[];
	const zoom = 1 + 0.06 * ramp(t, 0, dur('s07_nosignal'), Easing.linear);
	const lerp2 = (k: number) => [A[0] + (B[0] - A[0]) * k, A[1] + (B[1] - A[1]) * k];
	// a message tries to go and fails
	const msgK = 0.28 * ramp(t, e.messages - 0.3, e.no - 0.05, Easing.inOut(Easing.cubic));
	const msgO = win(t, e.messages - 0.35, e.no + 0.7, 0.25, 0.5);
	const fail = win(t, e.no - 0.05, e.no + 1.2, 0.08, 0.4);
	const mp = lerp2(msgK);
	// notes travel at light speed
	const trav = ramp(t, e.send_t, e.arrive_t, Easing.linear);
	const np = lerp2(trav);
	const notesO = win(t, e.send_t - 0.1, e.arrive_t + 0.25, 0.25, 0.25);
	const years = Math.round((trav * 100000) / 1000) * 1000;
	const arrived = ramp(t, e.arrive_t, e.arrive_t + 0.4);
	const rows = win(t, e.each - 0.1, dur('s07_nosignal') + 1, 0.4);
	const Row: React.FC<{side: 'left' | 'right'; x: number; y: number; o: number}> = ({side, x, y, o}) => (
		<div style={{position: 'absolute', left: x, top: y, display: 'flex', gap: 10, opacity: o}}>
			{trials.map((tr, i) => (
				<Chip key={i} c={tr[side]} size={26} />
			))}
		</div>
	);
	return (
		<AbsoluteFill style={{background: '#000'}}>
			<AbsoluteFill style={{transform: `scale(${zoom})`}}>
				<Img src={staticFile('plates/galaxy_plate_post.png')} style={{width: 1920, height: 1080}} />
			</AbsoluteFill>
			<svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
				<line x1={A[0]} y1={A[1]} x2={B[0]} y2={B[1]} stroke="rgba(255,255,255,0.35)" strokeWidth={1.5} strokeDasharray="6 10" />
				{[A, B].map((p, i) => (
					<g key={i}>
						<circle cx={p[0]} cy={p[1]} r={9} fill={INK} opacity={0.95} />
						<circle cx={p[0]} cy={p[1]} r={18 + 6 * Math.sin(t * 3 + i)} fill="none" stroke={INK} strokeWidth={1.5} opacity={0.5} />
					</g>
				))}
			</svg>
			<div style={{position: 'absolute', left: A[0] - 140, top: A[1] + 26}}>
				<Tag title="Lab A" sub="here" size={22} />
			</div>
			<div style={{position: 'absolute', left: B[0] + 26, top: B[1] - 60}}>
				<Tag title="Lab B" sub="far away" size={22} />
			</div>
			{/* failed message */}
			<div style={{position: 'absolute', left: mp[0], top: mp[1], transform: `translate(-50%,-50%) translateY(${fail * 18}px)`, opacity: msgO * (1 - 0.5 * fail)}}>
				<Badge text="✉  Hello" o={1} x={0} y={0} size={20} />
			</div>
			<div style={{position: 'absolute', left: mp[0] - 40, top: mp[1] - 70, width: 80, textAlign: 'center', fontFamily: FONT, fontSize: 70, fontWeight: 300, color: '#FF6B6B', textShadow: '0 0 20px #FF6B6B', opacity: fail}}>✕</div>
			<div style={{position: 'absolute', left: 0, right: 0, top: 80, opacity: win(t, e.no + 0.05, e.each + 1.6, 0.3, 0.3)}}>
				<Tag title="No faster-than-light messages" sub="you cannot choose your result" align="center" panel size={28} />
			</div>
			{/* each side sees only random colors */}
			<Row side="left" x={A[0] - 180} y={A[1] - 120} o={rows * (1 - arrived * 0.0)} />
			<Row side="right" x={B[0] - 170} y={B[1] + 60} o={rows} />
			<div style={{position: 'absolute', left: 0, right: 0, top: 80, opacity: win(t, e.each + 1.6, e.send_t - 0.1, 0.3, 0.3)}}>
				<Tag title="Each lab sees only random colors" align="center" panel size={28} />
			</div>
			{/* notes at the speed of light */}
			<div style={{position: 'absolute', left: np[0], top: np[1], opacity: notesO}}>
				<div style={{position: 'absolute', left: -14, top: -14, width: 28, height: 28, borderRadius: 28, background: 'radial-gradient(circle, #fff 0%, #cfe3ff 35%, rgba(160,190,255,0) 70%)', boxShadow: '0 0 30px #9fc3ff'}} />
				<div style={{position: 'absolute', left: 26, top: 12, whiteSpace: 'nowrap', opacity: 1 - ramp(t, e.arrive_t - 1.0, e.arrive_t - 0.5)}}>
					<Tag title="Notes, at light speed" sub={`${years.toLocaleString('en-US')} years so far`} size={20} />
				</div>
			</div>
			<div style={{position: 'absolute', left: 0, right: 0, top: 80, opacity: win(t, e.send_t, e.arrive_t, 0.3, 0.2)}}>
				<Tag title="To see the pattern, they must compare notes" sub="and notes cannot travel faster than light" align="center" panel size={28} />
			</div>
			{/* arrival: lists side by side reveal the pattern */}
			<Row side="left" x={B[0] - 170} y={B[1] + 102} o={arrived} />
			<div style={{position: 'absolute', left: 0, right: 0, top: 80, opacity: arrived}}>
				<Tag title="Pattern revealed: always opposite" align="center" panel size={28} />
			</div>
		</AbsoluteFill>
	);
};

// ================================================================= S08 Micius satellite
const S08: React.FC = () => {
	const t = useT();
	const f = useCurrentFrame() + 1;
	const e = EV.s08;
	const Sat = trackAt(TR08 as Track, f, 'Sat');
	const M0 = trackAt(TR08 as Track, f, 'marker0');
	const M1 = trackAt(TR08 as Track, f, 'marker1');
	const endT = dur('s08_real') + 1;
	return (
		<AbsoluteFill>
			<Video name="s08_real" />
			<div style={{position: 'absolute', left: 0, right: 0, top: 84, opacity: win(t, e.real - 0.4, e.satellite - 0.3)}}>
				<Tag title="This is real" sub="an experiment in space, 2017" align="center" panel size={30} />
			</div>
			<Callout x={Sat[0]} y={Sat[1]} tx={Sat[0] + 160} ty={Sat[1] - 170} title="Micius satellite" sub="500 km up" o={win(t, e.satellite - 0.2, e.today + 0.2)} />
			<Callout x={M0[0]} y={M0[1]} tx={M0[0] + 110} ty={M0[1] + 90} title="Delingha" sub="ground station" o={win(t, e.two - 0.1, e.today + 1.5)} />
			<Callout x={M1[0]} y={M1[1]} tx={M1[0] - 110} ty={M1[1] + 90} title="Lijiang" sub="ground station" o={win(t, e.two + 0.1, e.today + 1.5)} align="right" />
			<Bracket a={M1} b={M0} text="1,203 km apart" o={win(t, e.kilometers - 0.5, e.today + 1.5)} off={40} />
			<div style={{position: 'absolute', left: 96, top: 84, opacity: win(t, e.today - 0.1, endT, 0.5)}}>
				<div style={{width: 64, height: 3, background: LAV, marginBottom: 18}} />
				<Tag title="Entanglement today" size={27} color={LAV} />
				<div style={{fontFamily: FONT, color: INK, fontSize: 30, fontWeight: 400, marginTop: 16, lineHeight: 1.55, textShadow: '0 2px 12px #000'}}>
					<div style={{opacity: ramp(t, e.computers - 0.9, e.computers - 0.5)}}>Quantum computers</div>
					<div style={{opacity: ramp(t, e.secure - 0.4, e.secure)}}>Ultra-secure communication</div>
					<div style={{opacity: 0.8 * ramp(t, e.secure + 0.3, e.secure + 0.8), fontSize: 23, lineHeight: 1.4}}>shared secret keys that reveal any spy listening in</div>
					<div style={{opacity: 0.8 * ramp(t, e.secure + 0.6, e.secure + 1.1), fontSize: 23, lineHeight: 1.4}}>(the messages themselves still travel normally)</div>
				</div>
			</div>
			<div style={{position: 'absolute', right: 40, bottom: 34, fontFamily: FONT, fontSize: 15, color: INK, opacity: 0.55 * win(t, e.satellite, endT, 0.5)}}>Yin et al., Science 356, 1140 (2017)</div>
		</AbsoluteFill>
	);
};

// ================================================================= S09 outro
const S09: React.FC = () => {
	const t = useT();
	const e = EV.s09;
	const endT = dur('s09_outro');
	const o = win(t, e.that + 0.1, endT + 1, 0.9);
	const credits = win(t, endT - 2.9, endT + 1, 0.6);
	return (
		<AbsoluteFill>
			<Video name="s09_outro" />
			<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', opacity: o}}>
				<div style={{fontFamily: FONT, color: INK, textAlign: 'center', transform: `translateY(${-150 + (1 - o) * 12}px)`}}>
					<div style={{fontSize: 80, letterSpacing: 24, fontWeight: 300, textTransform: 'uppercase', textShadow: '0 0 40px rgba(180,170,255,0.35)'}}>Quantum Entanglement</div>
					<div style={{width: 120, height: 2, background: LAV, margin: '26px auto', opacity: 0.8}} />
					<div style={{fontSize: 30, fontWeight: 400, letterSpacing: 1, opacity: 0.9}}>Undecided until measured. Linked across any distance.</div>
				</div>
			</AbsoluteFill>
			<div style={{position: 'absolute', left: 0, right: 0, bottom: 150, textAlign: 'center', fontFamily: FONT, color: INK, fontSize: 17, lineHeight: 1.7, opacity: 0.7 * credits}}>
				Sources: NobelPrize.org, Physics 2022 · Yin et al., Science 356, 1140 (2017)
				<br />
				Earth imagery: NASA Visible Earth, Blue Marble and Black Marble
			</div>
		</AbsoluteFill>
	);
};

// ================================================================= captions
const Captions: React.FC = () => {
	const f = useCurrentFrame();
	const t = f / FPS;
	const cur = (CAPS as {start: number; end: number; text: string}[]).find((c) => t >= c.start - 0.05 && t <= c.end + 0.05);
	const any = (CAPS as {start: number; end: number}[]).some((c) => t >= c.start - 0.6 && t <= c.end + 0.6);
	const o = cur ? win(t, cur.start - 0.06, cur.end + 0.06, 0.1, 0.12) : 0;
	return (
		<AbsoluteFill style={{pointerEvents: 'none'}}>
			<div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 260, background: 'linear-gradient(to bottom, rgba(0,0,0,0), rgba(0,0,0,0.5))', opacity: any ? 1 : 0, transition: 'none'}} />
			{cur ? (
				<div style={{position: 'absolute', left: 160, right: 160, bottom: 62, textAlign: 'center', fontFamily: FONT, fontSize: 44, fontWeight: 500, color: INK, letterSpacing: 0.2, lineHeight: 1.25, textShadow: '0 2px 14px rgba(0,0,0,0.95), 0 0 2px rgba(0,0,0,0.9)', opacity: o}}>
					{cur.text}
				</div>
			) : null}
		</AbsoluteFill>
	);
};

// ================================================================= dips to black between chapters
const Dips: React.FC = () => {
	const f = useCurrentFrame();
	const ids = ['s06_boxes', 's07_nosignal', 's08_real', 's09_outro'];
	let o = 0;
	for (const id of ids) {
		const c = sh(id).start;
		o = Math.max(o, interpolate(f, [c - 7, c, c + 7], [0, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
	}
	const total = EV.total_frames;
	o = Math.max(o, interpolate(f, [0, 10], [1, 0], {extrapolateRight: 'clamp'}), interpolate(f, [total - 30, total - 1], [0, 1], {extrapolateLeft: 'clamp'}));
	return <AbsoluteFill style={{background: '#000', opacity: o}} />;
};

export const Film: React.FC = () => {
	loadFonts();
	return (
		<AbsoluteFill style={{background: '#000'}}>
			<Audio src={staticFile('audio/soundtrack.wav')} />
			<Shot id="s01_birth"><S01 /></Shot>
			<Shot id="s02_pair"><S02 /></Shot>
			<Shot id="s03_apart"><S03 /></Shot>
			<Shot id="s04_measure"><S04 /></Shot>
			<Shot id="s05_repeat"><S05 /></Shot>
			<Shot id="s06_boxes"><S06 /></Shot>
			<Shot id="s07_nosignal"><S07 /></Shot>
			<Shot id="s08_real"><S08 /></Shot>
			<Shot id="s09_outro"><S09 /></Shot>
			<Captions />
			<Dips />
		</AbsoluteFill>
	);
};
