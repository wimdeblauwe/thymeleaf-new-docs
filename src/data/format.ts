export function formatDate(date: string | Date): string {
	return new Intl.DateTimeFormat('en-GB', { dateStyle: 'long', timeZone: 'UTC' }).format(new Date(date));
}
