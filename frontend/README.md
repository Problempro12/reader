# frontend

This template should help get you started developing with Vue 3 in Vite.

## Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Type Support for `.vue` Imports in TS

TypeScript cannot handle type information for `.vue` imports by default, so we replace the `tsc` CLI with `vue-tsc` for type checking. In editors, we need [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) to make the TypeScript language service aware of `.vue` types.

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Type-Check, Compile and Minify for Production

```sh
npm run build
```

## Структура файлов

- **package.json**: Файл с зависимостями и скриптами для npm.
- **vite.config.ts**: Конфигурация сборщика Vite.
- **tsconfig.json**: Конфигурация TypeScript.
- **src/**: Основная директория с исходным кодом.
  - **main.ts**: Точка входа в приложение.
  - **App.vue**: Корневой компонент приложения.
  - **router/**: Директория с маршрутизацией.
    - **index.ts**: Основные маршруты приложения.
  - **components/**: Директория с компонентами.
    - **AppHeader.vue**: Компонент заголовка приложения.
    - **AppFooter.vue**: Компонент подвала приложения.
  - **views/**: Директория с представлениями (страницами).
    - **HomeView.vue**: Главная страница.
    - **ProfileView.vue**: Страница профиля пользователя.
    - **SettingsView.vue**: Страница настроек.
  - **stores/**: Директория с хранилищами (Pinia).
    - **user.ts**: Хранилище для данных пользователя.
  - **types/**: Директория с типами TypeScript.
    - **index.ts**: Основные типы приложения.
  - **assets/**: Директория с ресурсами (изображения, стили и т.д.).
  - **content/**: Директория с контентом (например, Markdown-файлы).
    - **privacy_policy.md**: Политика конфиденциальности.
