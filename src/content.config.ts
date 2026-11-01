import { defineCollection, z } from 'astro:content';
import { file } from 'astro/loaders';
import { docsLoader } from '@astrojs/starlight/loaders';
import { docsSchema } from '@astrojs/starlight/schema';

export const collections = {
	docs: defineCollection({ loader: docsLoader(), schema: docsSchema() }),
	ecosystem: defineCollection({
		loader: file('src/data/ecosystem.yaml'),
		schema: z.object({
			name: z.string(),
			description: z.string(),
			url: z.url(),
			category: z.enum([
				'official',
				'dialects',
				'ui-components',
				'interactivity',
				'front-end-tooling',
				'starters',
				'other-integrations',
			]),
			maintainer: z.string(),
			licence: z.string(),
			compatibility: z.string().optional(),
			docs: z.string().optional(),
			status: z.string().optional(),
			checked: z.coerce.date(),
		}),
	}),
};
