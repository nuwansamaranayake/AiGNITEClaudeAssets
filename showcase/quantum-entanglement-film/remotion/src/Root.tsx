import React from 'react';
import {Composition} from 'remotion';
import {Film} from './Film';
import EV from './data/events.json';

export const RemotionRoot: React.FC = () => (
	<Composition id="Film" component={Film} durationInFrames={EV.total_frames} fps={24} width={1920} height={1080} />
);
