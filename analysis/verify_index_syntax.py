for path in ['index.html', 'web_dashboard/index.html']:
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    assert 'id="totw-tab"' in c, f"totw-tab missing in {path}"
    assert 'totwData' in c, f"totwData missing in {path}"
    assert 'initTeamOfTheWeek' in c, f"initTeamOfTheWeek missing in {path}"
    assert "switchTab('totw'" in c, f"switchTab hook missing in {path}"
    assert '</main>' in c, f"</main> missing in {path}"
    assert '</html>' in c, f"</html> missing in {path}"
    print(f"[VERIFIED] {path} passed all integrity checks!")
