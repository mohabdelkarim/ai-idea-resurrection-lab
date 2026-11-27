# RFC: Top navigation bar for multipage apps

Summary
------
Introduce a first‑class top navigation bar widget for Streamlit multipage applications. The new widget will be exposed as `st.topbar` and will render a horizontal bar above the main content area, providing navigation buttons, dropdown menus, and optional icons. It will integrate with Streamlit’s theming system, session state, and the version‑2 component API, allowing developers to create consistent, responsive navigation without resorting to custom HTML/CSS hacks.

Motivation
----------
Multipage Streamlit apps currently rely on the sidebar for navigation, which forces a vertical layout and consumes valuable screen real‑estate, especially on wide displays. Users increasingly expect a modern web‑app look with a top navigation bar (similar to Dash, Flask‑Admin, or custom React apps). The lack of a native top bar forces developers to embed raw HTML or third‑party components, leading to fragmented theming, maintenance burdens, and accessibility issues. Since Streamlit 1.30 the internal layout manager supports horizontal containers, the theming API is unified, and the component v2 bridge simplifies React integration. These advances remove the technical blockers that prevented a top bar implementation in 2019, making it feasible to add a stable, first‑class solution now.

Detailed Design
---------------
**Backend API**
- Add a new class `TopBar` in `streamlit/runtime/legacy_caching/topbar.py` inheriting from `BaseWidget`.
- Public function `st.topbar(items: List[TopBarItem], *, title: str | None = None, logo: str | None = None, height: int = 60, key: str | None = None) -> TopBar`.
- `TopBarItem` is a dataclass with fields `label: str`, `icon: str | None`, `callback: Callable | None`, `dropdown: List[TopBarItem] | None`.
- The function registers a component via `streamlit.components.v2` passing a JSON payload of items, title, logo, and height.
- Interaction events are sent back through the component bridge and stored in `session_state` under the provided key, enabling reactive callbacks.

**Frontend Implementation**
- Create a React component `TopBarContainer` in `frontend/src/components/TopBarContainer.tsx`.
- Register with the layout manager using the new horizontal slot `TOP_BAR`.
- Render a `nav` element with CSS variables `--st-topbar-height`, `--st-primary-color`, etc., sourced from Streamlit’s theming context.
- Use React 18 concurrent features to lazily load icons and dropdown menus, ensuring smooth updates.
- Emit click events via `Streamlit.setComponentValue` to the backend.

**Layout Integration**
- Extend `LayoutManager` to reserve a fixed height region at the top when a `TopBar` component is present.
- Adjust the main content pane’s `margin-top` dynamically based on the measured height (default 60px) to avoid overlap.
- Support responsive collapse: on screens < 600px the bar collapses into a hamburger menu automatically.

**Styling & Theming**
- Leverage existing theming variables (`primaryColor`, `backgroundColor`, `textColor`) and expose new CSS custom properties for hover/active states.
- Provide dark‑mode aware defaults; developers can override via `st.set_page_config(page_title=..., layout="wide", initial_sidebar_state="collapsed", theme={...})`.

**Testing & Documentation**
- Add unit tests for payload serialization, session‑state synchronization, and layout adjustments.
- End‑to‑end Selenium tests for click handling, dropdown interaction, and responsive behavior.
- Documentation page `api-reference/topbar.md` with examples, theming guide, and migration notes.

Drawbacks
---------
- Increases the core codebase size and adds a new layout slot, which may introduce subtle regressions in existing apps that rely on precise vertical sizing.
- The top bar consumes vertical space, potentially reducing the usable area for content on small screens; developers must handle responsive design.
- Requires additional maintenance for the React component and its CSS, adding to the maintainer workload.

Alternatives
-----------
1. **HTML/CSS hack** – Continue using `st.markdown` with raw HTML/CSS. This avoids core changes but suffers from theming inconsistency and limited interactivity.
2. **Third‑party component** – Publish a community‑maintained `streamlit-topbar` component. While viable, it would lack official support, version compatibility guarantees, and integration with the layout manager.
3. **Sidebar redesign** – Extend the existing sidebar to support a horizontal mode. This would require a more invasive redesign of the sidebar logic and would still conflict with the vertical navigation paradigm.

Unresolved Questions
--------------------
- How should the top bar behave when both a sidebar and a top bar are present? Should the layout manager allow both simultaneously or enforce one?
- What is the optimal default height and padding to balance aesthetics and content space across devices?
- Should we expose an API for custom React children (e.g., search boxes) beyond the predefined `TopBarItem` structure?
- How will accessibility (ARIA roles, keyboard navigation) be validated across the various interactive elements?
- What versioning policy will we adopt for breaking changes to the `st.topbar` signature?

---

*RFC generated by Resurrection Bot 🧬*
