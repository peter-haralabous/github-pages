/**
 * Creates a constructable stylesheet from a <link> tag.
 *
 * Lit can't use `link.sheet` directly because it's not constructable.
 */
function getConstructableSheet(sheetId: string) {
  const link = document.getElementById(sheetId) as HTMLLinkElement | null;
  // Create a new, empty, adoptable sheet
  const newSheet = new CSSStyleSheet();

  if (!link || !link.sheet) {
    console.warn(`Could not find or access stylesheet with id "${sheetId}"`);
    return newSheet;
  }

  try {
    const rulesText = Array.from(link.sheet.cssRules)
      .map((rule) => rule.cssText)
      .join('\n');
    newSheet.replaceSync(rulesText);
  } catch (e) {
    console.error(`CORS error: Cannot access rules for ${link.href}`, e);
  }
  return newSheet;
}

export const globalStyles = getConstructableSheet('global_styles');
