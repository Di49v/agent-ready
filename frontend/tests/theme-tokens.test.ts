import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const css = readFileSync(new URL("../src/app/globals.css", import.meta.url), "utf8");
const lightTheme = css.match(/:root,\s*\[data-theme="light"\]\s*\{([\s\S]*?)\n\}/)?.[1];
const darkTheme = css.match(/\[data-theme="dark"\]\s*\{([\s\S]*?)\n\}/)?.[1];

const token = (theme: string | undefined, name: string) => {
  const value = theme?.match(new RegExp(`--${name}:\\s*(#[0-9A-Fa-f]{6})`))?.[1];
  if (!value) throw new Error(`Missing hex token --${name}`);
  return value;
};

const luminance = (hex: string) => {
  const channels = hex.slice(1).match(/.{2}/g)!.map((channel) => {
    const value = parseInt(channel, 16) / 255;
    return value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
  });
  return channels[0] * 0.2126 + channels[1] * 0.7152 + channels[2] * 0.0722;
};

const contrast = (foreground: string, background: string) => {
  const values = [luminance(foreground), luminance(background)].sort((a, b) => b - a);
  return (values[0] + 0.05) / (values[1] + 0.05);
};

describe("theme color tokens", () => {
  it("defines the neutral audit-instrument light palette", () => {
    expect(lightTheme).toBeDefined();
    expect(lightTheme).toMatch(/--bg:\s*#F4F3EE/i);
    expect(lightTheme).toMatch(/--surface:\s*#FBFAF6/i);
    expect(lightTheme).toMatch(/--surface-sunken:\s*#ECEAE3/i);
    expect(lightTheme).toMatch(/--border:\s*#DAD7CC/i);
    expect(lightTheme).toMatch(/--accent:\s*#14724B/i);
    expect(lightTheme).toMatch(/--text:\s*#14151A/i);
    expect(lightTheme).toMatch(/--text-heading:\s*#14151A/i);
    expect(lightTheme).toMatch(/--ledger-paypal:\s*#2F5F9E/i);
    expect(lightTheme).toMatch(/--ledger-store:\s*#6B614A/i);
  });

  it("defines the neutral audit-instrument dark palette", () => {
    expect(darkTheme).toBeDefined();
    expect(darkTheme).toMatch(/--bg:\s*#08090C/i);
    expect(darkTheme).toMatch(/--surface:\s*#0F1217/i);
    expect(darkTheme).toMatch(/--surface-sunken:\s*#0B0D11/i);
    expect(darkTheme).toMatch(/--border:\s*#1C2028/i);
    expect(darkTheme).toMatch(/--accent:\s*#56C98A/i);
    expect(darkTheme).toMatch(/--text:\s*#E9EAEE/i);
    expect(darkTheme).toMatch(/--text-heading:\s*#E9EAEE/i);
    expect(darkTheme).toMatch(/--ledger-paypal:\s*#8FB0DA/i);
    expect(darkTheme).toMatch(/--ledger-store:\s*#D9D3C3/i);
  });

  it("keeps status and terminal surfaces on distinct semantic tokens", () => {
    expect(darkTheme).toBeDefined();
    expect(darkTheme).toMatch(/--fail:\s*#F2675F/i);
    expect(darkTheme).toMatch(/--fail-soft:\s*rgba\(242, 103, 95, 0\.10\)/i);
    expect(darkTheme).toMatch(/--pass:\s*#56C98A/i);
    expect(darkTheme).toMatch(/--warn-border:\s*rgba\(224, 169, 59, 0\.28\)/i);
    expect(darkTheme).toMatch(/--code-bg:\s*#0A0C10/i);
    expect(darkTheme).toMatch(/--code-text:\s*#C9CCD6/i);
    expect(css).toMatch(/--color-warn-border:\s*var\(--warn-border\)/);
    expect(css).toMatch(/--color-ledger-paypal:\s*var\(--ledger-paypal\)/);
    expect(css).toMatch(/--color-ledger-store:\s*var\(--ledger-store\)/);
    expect(css).not.toMatch(/--(?:color-)?info(?:-soft)?:/);
    expect(css).not.toMatch(/--(?:bg-canvas|bg-panel|bg-card-hover|border-subtle|text-main|signal-[a-z]+|accent-telemetry):/);
  });

  it("scopes the additional section and card spacing to dark mode", () => {
    expect(css).toMatch(/\[data-theme="dark"\]\s+\.landing-dark-spacing/);
    expect(css).toMatch(/\[data-theme="dark"\]\s+\.workbench-dark-spacing/);
  });

  it("meets WCAG AA for text and semantic foregrounds on theme surfaces", () => {
    for (const theme of [lightTheme, darkTheme]) {
      expect(theme).toBeDefined();
      const textColors = ["text", "text-heading", "text-muted", "text-dim"];
      const backgrounds = ["bg", "surface-sunken", "surface", "surface-hover", "code-bg"];

      for (const foreground of textColors) {
        for (const background of backgrounds) {
          expect(
            contrast(token(theme, foreground), token(theme, background)),
            `--${foreground} on --${background}`
          ).toBeGreaterThanOrEqual(4.5);
        }
      }

      expect(contrast(token(theme, "code-text"), token(theme, "code-bg"))).toBeGreaterThanOrEqual(4.5);
      expect(contrast(token(theme, "accent-foreground"), token(theme, "accent"))).toBeGreaterThanOrEqual(4.5);
      for (const ledger of ["ledger-paypal", "ledger-store"]) {
        for (const background of ["bg", "surface-sunken", "surface", "surface-hover", "code-bg"]) {
          expect(
            contrast(token(theme, ledger), token(theme, background)),
            `--${ledger} on --${background}`
          ).toBeGreaterThanOrEqual(4.5);
        }
      }
      for (const semantic of ["pass", "fail", "warn"]) {
        for (const background of ["bg", "surface-sunken", "surface", "surface-hover"]) {
          expect(
            contrast(token(theme, semantic), token(theme, background)),
            `--${semantic} on --${background}`
          ).toBeGreaterThanOrEqual(4.5);
        }
      }
    }
  });
});
