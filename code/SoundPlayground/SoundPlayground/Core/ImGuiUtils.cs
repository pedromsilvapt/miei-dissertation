using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using System.Text;
using ImGuiNET;

namespace SoundPlayground.Core
{

    public enum SpecialKey
    {
        Win = 0,
        Shift = 1,
        ShiftRight = 2,
        Ctrl = 3,
        CtrlRight = 4,
        Alt = 5,
        AltGr = 6,
        Up = 45,
        Down = 46,
        Left = 47,
        Right = 48,
        Return = 49,
        Escape = 50,
        Space = 51,
        Tab = 52,
        Backspace = 53,
        Delete = 55,
        CapsLock = 60,
        MinusNumpad = 79,
        PlusNumpad = 80,
        Plus = 122,
        Minus = 128,

        // Letters
        A = 83,
        B = 84,
        C = 85,
        D = 86,
        E = 87,
        F = 88,
        G = 89,
        H = 90,
        I = 91,
        J = 92,
        K = 93,
        L = 94,
        M = 95,
        N = 96,
        O = 97,
        P = 98,
        Q = 99,
        R = 100,
        S = 101,
        T = 102,
        U = 103,
        V = 104,
        W = 105,
        X = 106,
        Y = 107,
        Z = 108
    }

    public static class ImGuiUtils
    {
        public static int ButtonToolbar(int count)
        {
            return ButtonToolbar(count, ImGui.GetContentRegionAvail().X);
        }

        public static int ButtonToolbar(int count, float width)
        {
            int buttonWidth = (int)width / count - ((int)ImGui.GetStyle().FramePadding.X * 2);

            return buttonWidth;
        }

        public static Vector2 CalcButtonSize(string label)
        {
            Vector2 size = ImGui.CalcTextSize(label);

            return size + ImGui.GetStyle().ItemInnerSpacing * 2;
        }

        public static float CalcInputWidth(string label)
        {
            return CalcInputWidth(label, ImGui.GetContentRegionAvail().X);
        }

        public static float CalcInputWidth(string label, float maxWidth)
        {
            return maxWidth - ImGui.CalcTextSize(label).X - ImGui.GetStyle().ItemInnerSpacing.X;
        }

        public static int HotkeyCharIndex(char key)
        {
            return key - 14;
        }

        public static bool Hotkey(char key)
        {
            return Hotkey(HotkeyCharIndex(key));
        }

        public static bool Hotkey(SpecialKey key)
        {
            return Hotkey((int)key);
        }

        public static bool Hotkey(SpecialKey key1, char key2)
        {
            return Hotkey((int)key1, HotkeyCharIndex(key2));
        }

        public static bool Hotkey(SpecialKey key1, SpecialKey key2, char key3)
        {
            return Hotkey((int)key1, (int)key2, HotkeyCharIndex(key3));
        }

        public static bool Hotkey(SpecialKey key1, SpecialKey key2, SpecialKey key3, char key4)
        {
            return Hotkey((int)key1, (int)key2, (int)key3, HotkeyCharIndex(key4));
        }

        public static bool Hotkey(params SpecialKey[] index)
        {
            return Hotkey(false, index.Select(i => (int)i).ToArray());
        }

        public static bool Hotkey(params int[] index)
        {
            return Hotkey(false, index);
        }

        public static bool Hotkey(bool global, params int[] index)
        {
            if (!global && !ImGui.IsWindowFocused())
            {
                return false;
            }

            int sum = 0;

            foreach (int i in index)
            {
                if (ImGui.IsKeyPressed(i, false))
                {
                    sum += 1;
                }
                else if (ImGui.IsKeyDown(i))
                {
                    sum += 2;
                }
                else
                {
                    return false;
                }
            }

            return sum == index.Length * 2 - 1;
        }

        public static bool BufferingBar(string label, float value)
        {
            return BufferingBar(label, value, new Vector2(ImGui.GetContentRegionAvail().X, 6));
        }

        public static bool BufferingBar(string label, float value, Vector2 sizeArg)
        {
            Vector4 bgCol = ImGui.ColorConvertU32ToFloat4(ImGui.GetColorU32(ImGuiCol.Button));
            Vector4 fgCol = ImGui.ColorConvertU32ToFloat4(ImGui.GetColorU32(ImGuiCol.ButtonHovered));

            return BufferingBar(label, value, sizeArg, bgCol, fgCol);
        }

        public static bool BufferingBar(string label, float value, Vector4 bgCol, Vector4 fgCol)
        {
            return BufferingBar(label, value, new Vector2(ImGui.GetContentRegionAvail().X - ImGui.GetStyle().FramePadding.X, 6), bgCol, fgCol);
        }

        public static bool BufferingBar(string label, float value, Vector2 sizeArg, Vector4 bgCol, Vector4 fgCol)
        {
            value = Math.Clamp(value, 0, 1);

            //ImGuiWindow* window = GetCurrentWindow();
            //if (window->SkipItems)
            //    return false;

            ImGuiStylePtr style = ImGui.GetStyle();
            uint id = ImGui.GetID(label);

            Vector2 pos = ImGui.GetWindowPos() + ImGui.GetCursorPos() - new Vector2(ImGui.GetScrollX(), ImGui.GetScrollY());
            Vector2 size = sizeArg;
            size.X -= style.FramePadding.X * 2;

            //const ImRect bb(pos, ImVec2(pos.x +size.x, pos.y + size.y));
            //ItemSize(bb, style.FramePadding.y);
            //if (!ItemAdd(bb, id))
            //    return false;

            // Render
            float circleStart = size.X * (0.7f + 0.3f * value);
            float circleEnd = size.X;
            float circleWidth = circleEnd - circleStart;

            uint bgColorInt = ImGui.ColorConvertFloat4ToU32(bgCol);
            uint fgColorInt = ImGui.ColorConvertFloat4ToU32(fgCol);

            ImGui.GetWindowDrawList().AddRectFilled(pos, new Vector2(pos.X + circleStart, pos.Y + size.Y), bgColorInt);
            ImGui.GetWindowDrawList().AddRectFilled(pos, new Vector2(pos.X + circleStart * value, pos.Y + size.Y), fgColorInt);


            float t = (float)ImGui.GetTime();
            float r = size.Y / 2;
            float speed = 1.5f;

            float a = speed * 0;
            float b = speed * 0.333f;
            float c = speed * 0.666f;

            float o1 = (circleWidth + r) * (t + a - speed * (int)((t + a) / speed)) / speed;
            float o2 = (circleWidth + r) * (t + b - speed * (int)((t + b) / speed)) / speed;
            float o3 = (circleWidth + r) * (t + c - speed * (int)((t + c) / speed)) / speed;

            ImGui.GetWindowDrawList().AddCircleFilled(new Vector2(pos.X + circleEnd - o1, pos.Y + r), r, bgColorInt);
            ImGui.GetWindowDrawList().AddCircleFilled(new Vector2(pos.X + circleEnd - o2, pos.Y + r), r, bgColorInt);
            ImGui.GetWindowDrawList().AddCircleFilled(new Vector2(pos.X + circleEnd - o3, pos.Y + r), r, bgColorInt);

            ImGui.SetCursorPos(new Vector2(style.WindowPadding.X, ImGui.GetCursorPos().Y + size.Y + style.FramePadding.Y));

            return true;
        }

        public static void PushDisabled(bool active)
        {
            if (active) PushDisabled();
        }

        public static void PushDisabled()
        {
            //ImGui.PushItemFlag(ImGuiItemFlags_Disabled, true);
            ImGui.PushStyleVar(ImGuiStyleVar.Alpha, ImGui.GetStyle().Alpha * 0.5f);
        }

        public static void PopDisabled(bool active)
        {
            if (active) PopDisabled();
        }

        public static void PopDisabled()
        {
            //ImGui.PopItemFlag();
            ImGui.PopStyleVar();
        }

        public static Stack<Vector2> CursorPosStack { get; set; } = new Stack<Vector2>();

        public static void PushCursorPos(Vector2 pos)
        {
            CursorPosStack.Push(ImGui.GetCursorPos());

            ImGui.SetCursorPos(pos);
        }

        public static Vector2 PopCursorPos()
        {
            Vector2 previous = CursorPosStack.Pop();

            Vector2 current = ImGui.GetCursorPos();

            ImGui.SetCursorPos(previous);

            return current;
        }

        public static Vector2 PeekCursorPos()
        {
            return CursorPosStack.Peek();
        }

        public static void InputTextPlaceholder(Vector2 pos, string placeholder, bool visible = true)
        {
            if (!visible) return;

            PushCursorPos(pos);

            ImGui.AlignTextToFramePadding();
            ImGui.SetCursorPosX(ImGui.GetCursorPosX() + ImGui.GetStyle().FramePadding.X);

            ImGui.TextDisabled(placeholder);
            
            PopCursorPos();
        }
    }
}
