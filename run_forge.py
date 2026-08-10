import asyncio
import fabric


def main():
    print("Booting Forge Engine...")
    kernel = fabric.boot_forge()
    overseer = kernel.overseer
    running = True

    print("System booted OK")
    print("Commands: status, stats, exit")
    print("-" * 40)

    async def engine_loop():
        nonlocal running
        while running:
            try:
                kernel.tick()
                for f in overseer.drain_findings():
                    print(f"[Finding] {f}")
            except Exception:
                pass
            await asyncio.sleep(0.1)

    async def cli_loop():
        nonlocal running
        while True:
            cmd = (await asyncio.to_thread(input, "forge> ")).strip().lower()
            if not cmd:
                continue
            if cmd in ["exit", "quit"]:
                running = False
                print("Session closed.")
                break
            elif cmd in ["status", "stats"]:
                print(f"Kernel:   {kernel.stats}")
                print(f"Overseer: {overseer.stats}")
            else:
                print(f"Unknown: {cmd}")
                print("Commands: status, stats, exit")

    async def start():
        await asyncio.gather(engine_loop(), cli_loop())

    try:
        asyncio.run(start())
    except (KeyboardInterrupt, SystemExit):
        print("Closed.")


if __name__ == "__main__":
    main()
