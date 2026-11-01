// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import starlightLinksValidator from 'starlight-links-validator';

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
			plugins: [
				// Converted pages link to each other with relative URLs, because root-relative
				// links break under the /thymeleaf-new-docs base path. The validator skips
				// relative links entirely when this is off (and reports them all when on), so
				// scripts/migrate-content/check_links.py verifies them in the built output.
				starlightLinksValidator({ errorOnRelativeLinks: false }),
			],
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
				{
					label: 'Using Thymeleaf',
					items: [{ autogenerate: { directory: 'docs/tutorials/using-thymeleaf' } }],
				},
				{
					label: 'Thymeleaf + Spring',
					items: [{ autogenerate: { directory: 'docs/tutorials/thymeleaf-spring' } }],
				},
				{
					label: 'Extending Thymeleaf',
					items: [{ autogenerate: { directory: 'docs/tutorials/extending-thymeleaf' } }],
				},
				{
					label: 'Articles',
					items: [{ autogenerate: { directory: 'docs/articles' } }],
				},
			],
		}),
	],
});
