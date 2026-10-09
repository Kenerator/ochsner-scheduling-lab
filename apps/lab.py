"""Local Scheduling Lab: explicit chat submission delegates to the shared core."""
import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full", app_title="Scheduling Lab")


@app.cell
def _():
    import os
    from html import escape
    from pathlib import Path
    import marimo as mo
    from appointment_assistant.ui_adapter import FormAdapter, create_session
    return FormAdapter, Path, create_session, escape, mo, os


@app.cell
def _(FormAdapter, Path, create_session, os):
    mode = os.environ.get("SCHEDULING_MODE", "openai")
    api_base = os.environ.get("API_BASE", "http://127.0.0.1:4013")
    model = os.environ.get("OPENAI_MODEL", "gpt-5.4-mini")
    session = create_session(mode, api_base, model)
    adapter = FormAdapter(session)
    asset_root = Path(__file__).resolve().parents[1] / "assets" / "ui"
    return adapter, asset_root, mode, model


@app.cell
def _(asset_root, mo):
    _tokens = (asset_root / "ochsner-observed-theme.css").read_text()
    mo.Html("<style>" + _tokens + """
    body { background: #f3f6fa; color: var(--text); font-family: var(--font-ui); }
    .lab-header { border-top: 6px solid var(--brand-primary); border-bottom: 3px solid var(--brand-accent); padding: 18px 4px; }
    .lab-badge { background: #13477d; color: white; border-radius: 6px; padding: 5px 12px; font-size: .85rem; font-weight: 650; }
    .lab-note { border-left: 4px solid var(--brand-accent); padding: 10px 16px; background: white; }
    :focus-visible { outline: 3px solid #13477d !important; outline-offset: 3px; }
    button:focus-visible, textarea:focus-visible { box-shadow: 0 0 0 5px #e0a42e80; }
    </style>""")
    return


@app.cell
def _(asset_root, mo, mode):
    _badge = "LIVE AI · OpenAI" if mode == "openai" else "DETERMINISTIC REHEARSAL · Simulation"
    mo.vstack([
        mo.hstack([
            mo.image(str(asset_root / "ochsner-health-observed.svg"), alt="Ochsner Health", width=210),
            mo.Html('<span class="lab-badge">' + _badge + '</span>'),
        ], align="center", justify="space-between").style({"border-bottom":"3px solid #e0a42e", "padding":"12px 0"}),
        mo.md("# Scheduling Lab"),
        mo.md("Find providers, book an appointment, or look up existing appointments through conversation."),
        mo.Html('<div class="lab-note"><strong>AI scheduling assistant · synthetic data only.</strong> '
                'Live mode uses OpenAI to interpret your message; rehearsal is deterministic simulation. '
                'The local scheduling API supplies facts. Dates and times use the displayed fixed −05:00 offset. '
                'After reviewing an exact booking summary, send <strong>yes</strong> or <strong>confirm</strong> '
                'in a separate message. This assistant provides no medical advice.</div>'),
    ], gap=0.5)
    return


@app.cell
def _(mo):
    get_submission_revision, set_submission_revision = mo.state(0)
    return get_submission_revision, set_submission_revision


@app.cell
def _(adapter, mo, set_submission_revision):
    def _on_submit(text):
        if text is not None:
            adapter.submit(text)
            set_submission_revision(lambda previous: previous + 1)

    request_form = mo.ui.text_area(
        placeholder="For example: Find primary care providers downtown",
        label="Your scheduling message",
        max_length=4000,
        # Publish edits to the wrapped input immediately; only form Send submits.
        debounce=False,
        rows=3,
        full_width=True,
    ).form(
        on_change=_on_submit,
        submit_button_label="Send message",
        clear_on_submit=True,
        bordered=False,
    )
    return (request_form,)


@app.cell
def _(adapter, escape, get_submission_revision, mo):
    # State changes only after an explicit form callback. These reads never submit.
    _revision = get_submission_revision()
    _turns = adapter.transcript()
    _bubbles = []
    for _user, _reply in _turns:
        _bubbles.extend([
            mo.Html('<div style="white-space:pre-wrap;background:#eaf2fa;padding:12px;border-radius:8px"><strong>You</strong><br>' + escape(_user) + '</div>'),
            mo.Html('<div style="white-space:pre-wrap;background:white;padding:12px;border-radius:8px;border-left:3px solid #13477d"><strong>AI scheduling assistant</strong><br>' + escape(_reply) + '</div>'),
        ])
    if not _bubbles:
        _bubbles = [mo.md("**How can I help?** Find providers, book an appointment, or look up your appointments.")]
    _inspector_body = mo.vstack([
        mo.md("### Developer evidence"),
        mo.md("Proposed actions, safety guard decisions and API outcomes. This view contains only the approved nonidentity evidence projection."),
        mo.json(adapter.evidence()).style({"max-height":"400px", "overflow":"auto", "min-width":"0", "width":"100%"}),
        mo.md("Session memory only. A queued mock handoff does not confirm human contact. Unknown effects require reconciliation before retrying."),
    ], gap=1).style({"background":"white", "padding":"18px", "border-radius":"10px", "border-top":"4px solid #13477d", "min-width":"0", "width":"100%", "box-sizing":"border-box", "overflow":"hidden"})
    # Keep the outer stack unstyled so Marimo gives its flex wrapper min-width:0.
    _inspector = mo.vstack([_inspector_body])
    mo.hstack([
        mo.vstack([
            mo.md("### Conversation"),
            mo.vstack(_bubbles, gap=1).style({"max-height":"500px", "overflow":"auto", "min-width":"0", "width":"100%", "overflow-wrap":"anywhere"}),
        ], gap=1),
        _inspector,
    ], widths=[3,2], align="start", gap=2)
    return


@app.cell
def _(mo, request_form):
    # The input lives in a stable output cell: transcript/evidence revisions must
    # never remount its DOM or detach Marimo's element-ID input subscription.
    mo.vstack([
        request_form,
        mo.md("Press **Send message** to submit, then wait for the response. Editing does not submit. Send **reset** as a separate message to start over; it cannot resolve unknown effects."),
    ], gap=0.5)
    return


if __name__ == "__main__":
    app.run()

