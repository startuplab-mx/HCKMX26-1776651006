import { Composition } from "remotion";
import { NahualDemo } from "./NahualDemo";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="NahualDemo"
      component={NahualDemo}
      durationInFrames={5400}
      fps={30}
      width={1920}
      height={1080}
    />
  );
};
