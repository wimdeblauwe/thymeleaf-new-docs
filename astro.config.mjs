// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	site: 'https://wimdeblauwe.github.io',
	base: '/thymeleaf-new-docs',
	integrations: [
		starlight({
			title: 'Thymeleaf',
			description: 'An independent proposal for new Thymeleaf documentation.',
			logo: { src: './src/assets/thymeleaf-mark.png', alt: '' },
			favicon: '/favicon.ico',
			// This demo must not compete with thymeleaf.org in search results.
			head: [{ tag: 'meta', attrs: { name: 'robots', content: 'noindex' } }],
			customCss: ['./src/styles/starlight.css'],
			components: {
				Banner: './src/components/StarlightBanner.astro',
				Footer: './src/components/StarlightFooter.astro',
			},
			social: [
				{
					icon: 'github',
					label: 'Proposal on GitHub',
					href: 'https://github.com/wimdeblauwe/thymeleaf-new-docs',
				},
			],
			sidebar: [
				{
					label: 'Start here',
					items: [{ autogenerate: { directory: 'docs/start' } }],
				},
			],
		}),
	],
});
