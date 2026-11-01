import examples from './home-examples.md?raw';

/** Returns a code block from home-examples.md, so the page shows what the tests run. */
export function homeExample(title: string): string {
	const block = examples
		.split(/^```/m)
		.find((part) => part.startsWith(`html title="${title}"`) || part.startsWith(`java title="${title}"`));
	if (!block) throw new Error(`No home example titled ${title}`);
	return block.slice(block.indexOf('\n') + 1).trimEnd();
}
