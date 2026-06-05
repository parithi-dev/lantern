# Lantern — Agent Guide

## Stack

- **Angular 22** standalone components (no `NgModule`). Bootstrap via `bootstrapApplication` in `src/main.ts`.
- **Application builder** (`@angular/build:application`) — not the old `@angular-devkit/build-angular`.
- **Vitest** via `@angular/build:unit-test` (not Karma). Test files use Jasmine-style `describe`/`it`/`expect` with `vitest/globals`.
- **TypeScript ~6.0.2** with `module: "preserve"`, strict mode, decorators. No `import.meta` etc.
- **SCSS** for component styles. Templates use external `.html` files.
- **Prettier** only — no ESLint. Format with `npx prettier --write .`.

## Commands

| Command | Action |
|---|---|
| `npm start` / `ng serve` | Dev server at `http://localhost:4200` |
| `npm test` / `ng test` | Run unit tests (Vitest) |
| `ng build` | Production build to `dist/` |
| `ng build --watch --configuration development` | Watch mode dev build |

## Conventions

- Single quotes, 100 print width, `angular` parser for HTML (see `.prettierrc`).
- Generate components/routing/pipes with `ng generate` (component style is `scss` by default).
- Route config lives in `src/app/app.routes.ts` (currently empty).
- Package manager is `npm@11.16.0` (per `packageManager` in `package.json`).

## Agent Skills

Relevant skills are available in `.agents/skills/` — load them when working with Angular patterns (DI, signals, forms, HTTP, directives, tooling, frontend design).

## Notes

- No CI workflows, no e2e test framework configured, no lint step.
- This is a fresh Angular CLI scaffold — replace the template content in `app.html`.
